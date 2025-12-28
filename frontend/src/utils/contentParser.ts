/**
 * 内容解析工具
 * 用于从纯文本中提取标题和正文，并过滤 AI 生成的标记
 */

export interface ParsedTitle {
  mainTitle?: string
  subTitle?: string
}

export interface ParsedImageSuggestion {
  bodyContent: string        // 正文内容（不含配图建议）
  imageSuggestion: string | null  // 配图建议内容，如果没有则返回 null
}

/**
 * 清理 AI 生成的页面类型标记
 * @param content 原始文本内容
 * @returns 清理后的文本
 */
export function cleanPageMarkers(content: string): string {
  if (!content) return content

  // 匹配 [封面]、[内容]、[总结] 标记（支持全角和半角括号）
  const markerPattern = /^\[?(封面|内容|总结)\]?[\s\u3000]*(?:\n|$)?/

  return content.replace(markerPattern, '').trim()
}

/**
 * 从封面内容中提取主标题和副标题
 * @param content 原始文本内容
 * @returns 主标题和副标题对象
 */
export function parseCoverTitles(content: string): ParsedTitle {
  if (!content || !content.trim()) {
    return {}
  }

  // 先清理 AI 标记（重要！）
  const cleaned = cleanPageMarkers(content)
  if (!cleaned) return {}

  const lines = cleaned.split('\n').filter(line => line.trim())

  // 查找"标题："和"副标题："关键词
  let mainTitle: string | undefined
  let subTitle: string | undefined

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()

    // 匹配"标题："或"标题："
    const titleMatch = line.match(/^标题[：:]\s*(.+)$/i)
    if (titleMatch && !mainTitle) {
      mainTitle = titleMatch[1].trim()
      continue
    }

    // 匹配"副标题："或"副标题："
    const subTitleMatch = line.match(/^副标题[：:]\s*(.+)$/i)
    if (subTitleMatch && !subTitle) {
      subTitle = subTitleMatch[1].trim()
      continue
    }

    // 如果没有找到关键词，第一行作为主标题，第二行作为副标题
    if (!mainTitle) {
      mainTitle = line
    } else if (!subTitle) {
      subTitle = line
    }
  }

  return { mainTitle, subTitle }
}

/**
 * 从文本中提取标题（第一行，清理后）
 * @param content 原始文本内容
 * @param pageType 页面类型（cover/content/summary）
 * @returns 标题文本，如果没有标题则返回 null
 */
export function parseTitle(content: string, pageType?: string): string | null {
  if (!content || !content.trim()) {
    return null
  }

  // 先清理 AI 标记
  const cleaned = cleanPageMarkers(content)

  if (!cleaned) return null

  // 封面类型：返回主标题
  if (pageType === 'cover') {
    const { mainTitle } = parseCoverTitles(cleaned)
    return mainTitle || null
  }

  // 其他类型：返回第一行
  const lines = cleaned.split('\n')
  const firstLine = lines[0]?.trim()

  if (!firstLine) {
    return null
  }

  return firstLine
}

/**
 * 从文本中提取正文（除第一行外的所有内容，清理后）
 * @param content 原始文本内容
 * @param pageType 页面类型（cover/content/summary）
 * @returns 正文文本，如果没有正文则返回空字符串
 */
export function parseBody(content: string, pageType?: string): string {
  if (!content || !content.trim()) {
    return ''
  }

  // 先清理 AI 标记
  const cleaned = cleanPageMarkers(content)

  if (!cleaned) return ''

  const lines = cleaned.split('\n')

  // 封面类型：移除主标题和副标题行
  if (pageType === 'cover') {
    const { mainTitle, subTitle } = parseCoverTitles(cleaned)

    // 找到标题行并移除
    let skipCount = 0
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim()

      // 跳过标题行
      if (mainTitle && line.includes(mainTitle) && (line.match(/^标题[：:]/i) || i === 0)) {
        skipCount++
        continue
      }

      // 跳过副标题行
      if (subTitle && line.includes(subTitle) && line.match(/^副标题[：:]/i)) {
        skipCount++
        continue
      }

      // 遇到非标题行，停止跳过
      break
    }

    const bodyLines = lines.slice(skipCount)
    return bodyLines.join('\n').trim()
  }

  // 其他类型：移除第一行（标题），保留剩余内容
  const bodyLines = lines.slice(1)

  if (bodyLines.length === 0) {
    return ''
  }

  return bodyLines.join('\n')
}

/**
 * 计算正文字数（不含标题和 AI 标记）
 * @param content 原始文本内容
 * @param pageType 页面类型（cover/content/summary）
 * @returns 正文字符数
 */
export function countBodyChars(content: string, pageType?: string): number {
  const body = parseBody(content, pageType)
  return body.length
}

/**
 * 判断文本是否有标题
 * @param content 原始文本内容
 * @param pageType 页面类型（cover/content/summary）
 * @returns 是否有标题
 */
export function hasTitle(content: string, pageType?: string): boolean {
  const title = parseTitle(content, pageType)
  return title !== null && title.length > 0
}

/**
 * 获取清理后的完整内容（移除 AI 标记）
 * @param content 原始文本内容
 * @returns 清理后的完整文本
 */
export function getCleanedContent(content: string): string {
  return cleanPageMarkers(content) || ''
}

/**
 * 从正文中提取配图建议
 * @param content 原始文本内容
 * @param pageType 页面类型（cover/content/summary）
 * @returns 解析后的正文和配图建议
 */
export function parseImageSuggestion(content: string, pageType?: string): ParsedImageSuggestion {
  // 1. 先获取正文（已移除标题和AI标记）
  const body = parseBody(content, pageType)

  if (!body) {
    return { bodyContent: '', imageSuggestion: null }
  }

  // 2. 查找配图建议标记（支持多种格式）
  // 封面页使用"背景："，其他页面使用"配图建议："
  const patterns = [
    /\n配图建议[：:]\s*/i,    // 配图建议：
    /\n背景[：:]\s*/i,        // 背景：
  ]

  let match: RegExpMatchArray | null = null

  for (const pattern of patterns) {
    const result = body.match(pattern)
    if (result) {
      match = result
      break
    }
  }

  if (!match) {
    // 没有找到配图建议，返回全部内容
    return { bodyContent: body, imageSuggestion: null }
  }

  // 3. 分离正文和配图建议
  const index = body.indexOf(match[0])
  const bodyContent = body.substring(0, index).trim()
  const imageSuggestion = body.substring(index + match[0].length).trim()

  return { bodyContent, imageSuggestion }
}
