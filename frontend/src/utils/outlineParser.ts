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
  // 使用 <page> 标签分割页面
  const pageTexts = accumulated.split(/<page>/i)

  return pageTexts
    .map((text, index) => {
      const trimmed = text.trim()
      if (!trimmed) return null

      // 识别页面类型（基于后端的解析逻辑）
      const typeMatch = trimmed.match(/^\[(\S+)\]/)
      let type: 'cover' | 'content' | 'summary' = 'content'
      let content = trimmed

      if (typeMatch) {
        const typeMapping: Record<string, 'cover' | 'content' | 'summary'> = {
          '封面': 'cover',
          '内容': 'content',
          '总结': 'summary'
        }
        type = typeMapping[typeMatch[1]] || 'content'
        // 移除类型标记，保留实际内容
        content = trimmed.replace(/^\[\S+\]\s*/, '')
      }

      return {
        index,
        type,
        content: content, // 使用去除类型标记后的内容
        streamingContent: '',
        isStreaming: false,
        isStreamComplete: false
      }
    })
    .filter((page): page is Page => page !== null)
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
