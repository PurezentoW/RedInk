import { defineStore } from 'pinia'
import type { Page } from '../api'
import { parsePagesFromText, detectNewPages, determineStreamingPage } from '../utils/outlineParser'

export interface SearchResult {
  title: string
  url: string
  snippet: string
  content: string
  source: string
}

export interface GeneratedImage {
  index: number
  url: string
  status: 'generating' | 'done' | 'error' | 'retrying'
  error?: string
  retryable?: boolean
}

/**
 * 规范化文案数据（向后兼容）
 * 处理旧的单标题数据，转换为新的多标题格式
 */
export function normalizeCopywriting(data: any): {
  raw: string
  title: string
  titles?: string[]
  content: string
  tags: string[]
} {
  // 如果没有 titles 数组或为空，从 title 字段生成单元素数组
  if (!data.titles || data.titles.length === 0) {
    if (data.title) {
      data.titles = [data.title]
    } else {
      data.titles = []
    }
  }

  // 如果没有 title 字段但有 titles 数组，默认选中第一个
  if (!data.title && data.titles.length > 0) {
    data.title = data.titles[0]
  }

  return data
}

export interface GeneratorState {
  // 当前阶段
  stage: 'input' | 'outline' | 'generating' | 'result'

  // 用户输入
  topic: string

  // 大纲数据
  outline: {
    raw: string
    pages: Page[]
  }

  // 流式生成状态（重构）
  isStreaming: boolean
  currentStreamingPageIndex: number  // 当前正在流式显示的页面索引
  allPagesStreamed: boolean          // 所有页面是否都已完成流式
  accumulatedText: string            // 累积的完整文本（用于解析页面）

  // 生成进度
  progress: {
    current: number
    total: number
    status: 'idle' | 'generating' | 'done' | 'error'
  }

  // 生成结果
  images: GeneratedImage[]

  // 任务ID
  taskId: string | null

  // 历史记录ID
  recordId: string | null

  // 用户上传的图片（用于图片生成参考）
  userImages: File[]

  // 搜索结果
  searchResults: SearchResult[]
  usedSearch: boolean

  // 文案数据
  copywriting: {
    raw: string
    title: string       // 当前选中的标题
    titles?: string[]   // 所有备选标题数组（新增，可选）
    content: string
    tags: string[]
  }

  // 文案流式生成状态
  isCopywritingStreaming: boolean
  copywritingAccumulatedText: string
}

const STORAGE_KEY = 'generator-state'

// 从 localStorage 加载状态
function loadState(): Partial<GeneratorState> {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (e) {
    console.error('加载状态失败:', e)
  }
  return {}
}

// 保存状态到 localStorage
function saveState(state: GeneratorState) {
  try {
    // 只保存关键数据，不保存 userImages（文件对象无法序列化）
    const toSave = {
      stage: state.stage,
      topic: state.topic,
      outline: state.outline,
      progress: state.progress,
      images: state.images,
      taskId: state.taskId,
      recordId: state.recordId,
      searchResults: state.searchResults,
      usedSearch: state.usedSearch
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
  } catch (e) {
    console.error('保存状态失败:', e)
  }
}

export const useGeneratorStore = defineStore('generator', {
  state: (): GeneratorState => {
    const saved = loadState()
    return {
      stage: saved.stage || 'input',
      topic: saved.topic || '',
      outline: saved.outline || {
        raw: '',
        pages: []
      },
      isStreaming: false,
      currentStreamingPageIndex: -1,
      allPagesStreamed: false,
      accumulatedText: '',
      progress: saved.progress || {
        current: 0,
        total: 0,
        status: 'idle'
      },
      images: saved.images || [],
      taskId: saved.taskId || null,
      recordId: saved.recordId || null,
      userImages: [],  // 不从 localStorage 恢复
      searchResults: saved.searchResults || [],
      usedSearch: saved.usedSearch || false,
      copywriting: saved.copywriting || {
        raw: '',
        title: '',
        content: '',
        tags: []
      },
      isCopywritingStreaming: false,
      copywritingAccumulatedText: ''
    }
  },

  actions: {
    // 设置主题
    setTopic(topic: string) {
      this.topic = topic
    },

    // 设置搜索结果
    setSearchResults(results: SearchResult[]) {
      this.searchResults = results
      this.usedSearch = true
    },

    // ========== 文案生成相关 ==========

    // 开始文案生成
    startCopywritingStreaming() {
      this.isCopywritingStreaming = true
      this.copywritingAccumulatedText = ''
      this.copywriting = {
        raw: '',
        title: '',
        content: '',
        tags: []
      }
    },

    // 更新文案流式文本
    updateCopywritingStreaming(chunk: string, accumulated: string) {
      this.copywritingAccumulatedText = accumulated
    },

    // 完成文案生成
    finishCopywritingStreaming(result: {
      raw: string
      title: string
      titles?: string[]
      content: string
      tags: string[]
    }) {
      // 规范化数据（向后兼容）
      const normalized = normalizeCopywriting(result)
      this.copywriting = normalized
      this.isCopywritingStreaming = false
      this.copywritingAccumulatedText = ''
      this.autoSaveCopywriting()
    },

    // 停止文案生成（错误处理）
    stopCopywritingStreaming() {
      this.isCopywritingStreaming = false
      this.copywritingAccumulatedText = ''
    },

    // 更新文案
    updateCopywriting(data: {
      raw?: string
      title?: string
      titles?: string[]
      content?: string
      tags?: string[]
    }) {
      this.copywriting = { ...this.copywriting, ...data }
      this.autoSaveCopywriting()
    },

    // 自动保存文案
    async autoSaveCopywriting() {
      if (!this.recordId) {
        // 如果没有 recordId，先创建记录
        await this.autoSaveDraft()
        return
      }

      try {
        const { updateHistory } = await import('../api')
        await updateHistory(this.recordId, {
          copywriting: this.copywriting
        })
        console.log('文案已保存到历史记录')
      } catch (error) {
        console.error('保存文案失败:', error)
      }
    },


    // 开始流式生成（重构）
    startStreaming(topic: string) {
      this.stage = 'outline'
      this.topic = topic
      this.isStreaming = true
      this.currentStreamingPageIndex = -1
      this.allPagesStreamed = false
      this.accumulatedText = ''
      this.outline.raw = ''
      this.outline.pages = []

      // 清除旧的搜索结果
      this.searchResults = []
      this.usedSearch = false
    },

    // 更新流式文本（核心逻辑）
    updateStreamingText(chunk: string, accumulated: string) {
      this.accumulatedText = accumulated

      // 重新解析所有页面
      const newPages = parsePagesFromText(accumulated)
      const oldPages = this.outline.pages

      // 检测新增页面
      const newIndices = detectNewPages(oldPages, newPages)

      // 添加新页面到 store
      for (const index of newIndices) {
        const newPage = newPages[index]
        newPage.isStreaming = true
        newPage.isStreamComplete = false
        newPage.streamingContent = ''

        this.outline.pages.push(newPage)

        console.log(`📄 新增页面 ${index}: ${newPage.type}, 内容:`, newPage.content.substring(0, 20))
      }

      // 从累积文本中提取所有页面内容
      const pageTexts = accumulated.split(/<page>/i).map(text => text.trim()).filter(text => text)

      // 更新所有已存在页面的流式内容
      this.outline.pages.forEach((page, idx) => {
        if (idx < pageTexts.length) {
          // 使用对应的页面文本更新流式内容
          page.streamingContent = pageTexts[idx]

          // 如果该页面正在流式中
          if (page.isStreaming) {
            this.currentStreamingPageIndex = idx

            // 检查是否是该页面的最后一段（检测是否有下一个页面）
            const isLastPage = idx === pageTexts.length - 1

            if (!isLastPage) {
              // 不是最后一页，说明该页面已完成
              page.isStreamComplete = true
              page.isStreaming = false
              page.content = page.streamingContent
              console.log(`✅ 页面 ${idx} 流式完成`)
            }
          }
        }
      })

      // 确定当前应该流式显示的页面
      const streamingIndex = determineStreamingPage(
        this.outline.pages,
        this.currentStreamingPageIndex
      )

      if (streamingIndex !== -1) {
        const page = this.outline.pages[streamingIndex]
        // 确保流式内容是最新的
        page.streamingContent = pageTexts[streamingIndex] || ''
      }
    },

    // 完成流式生成（重构）
    finishStreaming(result: {
      outline: string;
      pages: Page[];
      has_images?: boolean;
      used_search?: boolean;
      search_results?: any[]
    }) {
      this.outline.raw = result.outline
      this.outline.pages = result.pages

      // 标记所有页面为完成状态
      this.outline.pages.forEach(page => {
        page.isStreamComplete = true
        page.isStreaming = false
        page.content = page.content || page.streamingContent || ''
      })

      // 保存搜索结果
      this.searchResults = result.search_results || []
      this.usedSearch = result.used_search || false

      this.isStreaming = false
      this.currentStreamingPageIndex = -1
      this.allPagesStreamed = true
      this.accumulatedText = ''
      this.stage = 'outline'

      console.log('🎉 所有页面流式生成完成')
      if (this.usedSearch) {
        console.log(`🔍 收到 ${this.searchResults.length} 条搜索结果`)
      }
    },

    // 流式生成错误处理（新增）
    stopStreaming() {
      this.isStreaming = false
      this.currentStreamingPageIndex = -1
      this.allPagesStreamed = false
      this.accumulatedText = ''
    },

    // 设置大纲
    setOutline(raw: string, pages: Page[]) {
      this.outline.raw = raw
      this.outline.pages = pages
      this.stage = 'outline'
    },

    // 更新页面
    updatePage(index: number, content: string) {
      const page = this.outline.pages.find(p => p.index === index)
      if (page) {
        page.content = content
        // 同步更新 raw 文本
        this.syncRawFromPages()
      }
    },

    // 根据 pages 重新生成 raw 文本
    syncRawFromPages() {
      this.outline.raw = this.outline.pages
        .map(page => page.content)
        .join('\n\n<page>\n\n')
    },

    // 删除页面
    deletePage(index: number) {
      this.outline.pages = this.outline.pages.filter(p => p.index !== index)
      // 重新索引
      this.outline.pages.forEach((page, idx) => {
        page.index = idx
      })
      // 同步更新 raw 文本
      this.syncRawFromPages()
    },

    // 添加页面
    addPage(type: 'cover' | 'content' | 'summary', content: string = '') {
      const newPage: Page = {
        index: this.outline.pages.length,
        type,
        content
      }
      this.outline.pages.push(newPage)
      // 同步更新 raw 文本
      this.syncRawFromPages()
    },

    // 插入页面
    insertPage(afterIndex: number, type: 'cover' | 'content' | 'summary', content: string = '') {
      const newPage: Page = {
        index: afterIndex + 1,
        type,
        content
      }
      this.outline.pages.splice(afterIndex + 1, 0, newPage)
      // 重新索引
      this.outline.pages.forEach((page, idx) => {
        page.index = idx
      })
      // 同步更新 raw 文本
      this.syncRawFromPages()
    },

    // 移动页面 (拖拽排序)
    movePage(fromIndex: number, toIndex: number) {
      const pages = [...this.outline.pages]
      const [movedPage] = pages.splice(fromIndex, 1)
      pages.splice(toIndex, 0, movedPage)

      // 重新索引
      pages.forEach((page, idx) => {
        page.index = idx
      })

      this.outline.pages = pages
      // 同步更新 raw 文本
      this.syncRawFromPages()
    },

    // 开始生成
    startGeneration() {
      this.stage = 'generating'
      this.progress.current = 0
      this.progress.total = this.outline.pages.length
      this.progress.status = 'generating'
      this.images = this.outline.pages.map(page => ({
        index: page.index,
        url: '',
        status: 'generating'
      }))
    },

    // 更新进度
    updateProgress(index: number, status: 'generating' | 'done' | 'error', url?: string, error?: string) {
      const image = this.images.find(img => img.index === index)
      if (image) {
        image.status = status
        if (url) image.url = url
        if (error) image.error = error
      }
      if (status === 'done') {
        this.progress.current++
      }
    },

    updateImage(index: number, newUrl: string) {
      const image = this.images.find(img => img.index === index)
      if (image) {
        const timestamp = Date.now()
        image.url = `${newUrl}?t=${timestamp}`
        image.status = 'done'
        delete image.error
      }
    },

    // 完成生成
    finishGeneration(taskId: string) {
      this.taskId = taskId
      this.stage = 'result'
      this.progress.status = 'done'
    },

    // 设置单个图片为重试中状态
    setImageRetrying(index: number) {
      const image = this.images.find(img => img.index === index)
      if (image) {
        image.status = 'retrying'
      }
    },

    // 获取失败的图片列表
    getFailedImages() {
      return this.images.filter(img => img.status === 'error')
    },

    // 获取失败图片对应的页面
    getFailedPages() {
      const failedIndices = this.images
        .filter(img => img.status === 'error')
        .map(img => img.index)
      return this.outline.pages.filter(page => failedIndices.includes(page.index))
    },

    // 检查是否有失败的图片
    hasFailedImages() {
      return this.images.some(img => img.status === 'error')
    },

    // 重置
    reset() {
      this.stage = 'input'
      this.topic = ''
      this.outline = {
        raw: '',
        pages: []
      }
      this.isStreaming = false
      this.currentStreamingPageIndex = -1
      this.allPagesStreamed = false
      this.accumulatedText = ''
      this.progress = {
        current: 0,
        total: 0,
        status: 'idle'
      }
      this.images = []
      this.taskId = null
      this.recordId = null
      this.userImages = []
      this.searchResults = []
      this.usedSearch = false
      this.copywriting = {
        raw: '',
        title: '',
        content: '',
        tags: []
      }
      this.isCopywritingStreaming = false
      this.copywritingAccumulatedText = ''
      // 清除 localStorage
      localStorage.removeItem(STORAGE_KEY)
    },

    // 保存当前状态
    saveToStorage() {
      // 只保存关键数据，不保存 userImages（文件对象无法序列化）
      const toSave = {
        stage: this.stage,
        topic: this.topic,
        outline: this.outline,
        progress: this.progress,
        images: this.images,
        taskId: this.taskId,
        recordId: this.recordId,
        searchResults: this.searchResults,
        usedSearch: this.usedSearch,
        copywriting: this.copywriting  // 新增：保存文案数据
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
    },

    // 自动保存草稿到后端
    async autoSaveDraft() {
      // 如果没有主题或大纲内容，不保存
      if (!this.topic.trim() || !this.outline.pages.length) {
        return
      }

      try {
        // 动态导入 API 函数，避免循环依赖
        const { createHistory, updateHistory } = await import('../api')

        if (this.recordId) {
          // 更新现有记录
          await updateHistory(this.recordId, {
            outline: {
              raw: this.outline.raw,
              pages: this.outline.pages
            }
          })
          console.log('草稿已更新到后端')
        } else {
          // 创建新记录
          const result = await createHistory(
            this.topic,
            this.outline
          )
          if (result.success && result.record_id) {
            this.recordId = result.record_id
            console.log('草稿已创建到后端:', this.recordId)
          }
        }
      } catch (error) {
        console.error('自动保存草稿失败:', error)
        // 不抛出错误，静默失败
      }
    },

    // 手动触发保存（给用户明确的保存反馈）
    async manualSaveDraft() {
      await this.autoSaveDraft()
      return !!this.recordId
    }
  }
})

// 监听状态变化并自动保存（使用 watch）
import { watch } from 'vue'

export function setupAutoSave() {
  const store = useGeneratorStore()

  // 监听关键字段变化并自动保存
  watch(
    () => ({
      stage: store.stage,
      topic: store.topic,
      outline: store.outline,
      progress: store.progress,
      images: store.images,
      taskId: store.taskId,
      recordId: store.recordId
    }),
    () => {
      store.saveToStorage()
    },
    { deep: true }
  )
}
