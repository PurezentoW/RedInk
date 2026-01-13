/**
 * 大纲页面解析工具
 * 用于从流式文本中实时解析页面结构
 */

import type { Page } from '../api'

/**
 * 从累积文本中解析页面
 * @param accumulated 累积的完整大纲文本
 * @returns 解析后的页面数组
 */
export function parsePagesFromText(accumulated: string): Page[] {
  // 预处理：去除所有 </page> 闭合标签（新提示词格式）
  const cleaned = accumulated.replace(/<\/page>/gi, '')

  // 使用正则表达式匹配 <page> 标签之间的内容
  // 支持两种格式：
  // 1. <page> 在内容之前（新格式）：<page>[封面]内容<page>[内容]内容
  // 2. <page> 在内容之后（旧格式）：[封面]内容<page>[内容]内容<page>
  const pagePattern = /<page>\s*([^\0]*?)(?=<page>|$)/gi
  const matches = Array.from(cleaned.matchAll(pagePattern), m => m[1])

  // 如果没有匹配到任何内容（可能使用旧格式或没有<page>标签）
  if (matches.length === 0 && cleaned.trim()) {
    // 尝试旧格式：用 <page> 分割
    const fallbackTexts = cleaned.split(/<page>/i).filter(t => t.trim())
    if (fallbackTexts.length > 0) {
      return fallbackTexts.map((text, index) => parseSinglePage(text, index))
        .filter((page): page is Page => page !== null)
    }
  }

  return matches
    .map((text, index) => parseSinglePage(text, index))
    .filter((page): page is Page => page !== null)
}

/**
 * 解析单个页面
 * @param text 页面文本
 * @param index 页面索引
 * @returns 页面对象或 null
 */
function parseSinglePage(text: string, index: number): Page | null {
  // 去除所有 <page> 和 </page> 标签
  let cleaned = text.replace(/<\/?page>/gi, '').trim()

  if (!cleaned) return null

  // 识别页面类型（基于后端的解析逻辑）
  const typeMatch = cleaned.match(/^\[(\S+)\]/)
  let type: 'cover' | 'content' | 'summary' = 'content'
  let content = cleaned

  if (typeMatch) {
    const typeMapping: Record<string, 'cover' | 'content' | 'summary'> = {
      '封面': 'cover',
      '内容': 'content',
      '总结': 'summary'
    }
    type = typeMapping[typeMatch[1]] || 'content'
    // 移除类型标记，保留实际内容
    content = cleaned.replace(/^\[\S+\]\s*/, '')
  }

  return {
    index,
    type,
    content: content, // 使用去除类型标记后的内容
    streamingContent: '',
    isStreaming: false,
    isStreamComplete: false
  }
}

/**
 * 检测累积文本中新出现的页面
 * @param oldPages 之前的页面数组
 * @param newPages 新解析的页面数组
 * @returns 新增页面的索引数组
 */
export function detectNewPages(oldPages: Page[], newPages: Page[]): number[] {
  const newIndices: number[] = []

  for (const newPage of newPages) {
    const exists = oldPages.some(old => old.index === newPage.index)
    if (!exists) {
      newIndices.push(newPage.index)
    }
  }

  return newIndices
}

/**
 * 确定应该接收流式数据的页面
 * @param pages 所有页面
 * @param currentStreamingIndex 当前流式页面索引
 * @returns 应该流式显示的页面索引，-1表示所有页面都完成
 */
export function determineStreamingPage(pages: Page[], currentStreamingIndex: number): number {
  // 如果有页面正在流式中，继续
  const currentPage = pages[currentStreamingIndex]
  if (currentPage && !currentPage.isStreamComplete) {
    return currentStreamingIndex
  }

  // 否则找到第一个未完成的页面
  for (let i = 0; i < pages.length; i++) {
    if (!pages[i].isStreamComplete) {
      return i
    }
  }

  // 所有页面都已完成
  return -1
}
