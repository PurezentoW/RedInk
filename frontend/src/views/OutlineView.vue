<template>
  <div class="container" style="max-width: 100%;">
    <div class="page-header" style="max-width: 1200px; margin: 0 auto 30px auto;">
      <div>
        <h1 class="page-title">编辑大纲</h1>
        <p class="page-subtitle">
          调整页面顺序，修改文案，打造完美内容
          <span v-if="saveStatus" class="save-status" :class="saveStatus.type">
            {{ saveStatus.message }}
          </span>
        </p>
      </div>
      <div style="display: flex; gap: 12px;">
        <button
          class="btn btn-secondary"
          @click="goBack"
          :disabled="store.isStreaming"
          style="background: white; border: 1px solid var(--border-color);"
        >
          上一步
        </button>
        <button
          class="btn btn-primary"
          @click="startGeneration"
          :disabled="isSaving || store.isStreaming"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path><line x1="16" y1="8" x2="2" y2="22"></line><line x1="17.5" y1="15" x2="9" y2="15"></line></svg>
          {{ isSaving ? '保存中...' : '开始生成图片' }}
        </button>
      </div>
    </div>

    <!-- 流式生成进度提示（修改） -->
    <div v-if="store.isStreaming" class="streaming-progress-bar">
      <div class="spinner"></div>
      <span>AI 正在创作中... ({{ store.outline.pages.length }} 页)</span>
    </div>

    <!-- 搜索结果展示区域 -->
    <div
      v-if="shouldShowSearchResults"
      class="search-results-container"
    >
      <div class="search-results-header" @click="searchResultsExpanded = !searchResultsExpanded">
        <div class="search-results-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <span>网络搜索结果 ({{ store.searchResults.length }} 条)</span>
        </div>
        <button class="collapse-toggle-btn">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            :style="{ transform: searchResultsExpanded ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.3s' }"
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
      </div>

      <!-- 结果列表 - 根据 expanded 状态显示/隐藏 -->
      <div v-show="searchResultsExpanded" class="search-results-list">
        <div
          v-for="(result, index) in displayedSearchResults"
          :key="index"
          class="search-result-item"
        >
          <div class="result-header">
            <a :href="result.url" target="_blank" rel="noopener noreferrer" class="result-title">
              {{ result.title }}
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
            </a>
            <span class="result-source">{{ result.source }}</span>
          </div>
          <div class="result-snippet">{{ result.snippet }}</div>
        </div>
      </div>
    </div>

    <div class="outline-grid" :class="{ disabled: store.isStreaming }">
      <div
        v-for="(page, idx) in store.outline.pages"
        :key="page.index"
        class="card outline-card"
        :class="{
          'dragging-over': dragOverIndex === idx,
          'streaming-active': page.isStreaming
        }"
        draggable="true"
        @dragstart="onDragStart($event, idx)"
        @dragover.prevent="onDragOver($event, idx)"
        @dragenter.prevent
        @drop="onDrop($event, idx)"
        @dragend="() => { dragOverIndex = null; draggedIndex = null }"
      >
        <!-- 拖拽手柄 (改为右上角或更加隐蔽) -->
        <div class="card-top-bar">
          <div class="page-info">
             <span class="page-number">P{{ idx + 1 }}</span>
             <span class="page-type" :class="page.type">{{ getPageTypeName(page.type) }}</span>
             <!-- 流式状态指示器（新增） -->
             <span v-if="page.isStreaming" class="streaming-badge">
               <span class="streaming-dot"></span>
               生成中
             </span>
          </div>

          <div class="card-controls" :class="{ disabled: store.isStreaming }">
            <div class="drag-handle" title="拖拽排序">
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="1"></circle><circle cx="9" cy="5" r="1"></circle><circle cx="9" cy="19" r="1"></circle><circle cx="15" cy="12" r="1"></circle><circle cx="15" cy="5" r="1"></circle><circle cx="15" cy="19" r="1"></circle></svg>
            </div>
            <button
              class="icon-btn"
              :class="{ active: isEditingPage(page.index) }"
              @click="toggleEditPage(page.index)"
              title="编辑此页"
              :disabled="store.isStreaming"
            >
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            </button>
            <button
              class="icon-btn"
              @click="deletePage(idx)"
              title="删除此页"
              :disabled="store.isStreaming"
            >
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
        </div>

        <!-- 内容显示区域（修改） -->
        <div class="content-display">
          <ContentRenderer
            :raw-content="getContentForDisplay(page)"
            :is-streaming="page.isStreaming"
            :is-editing="isEditingPage(page.index)"
            :streaming-content="page.streamingContent"
            :page-type="page.type"
            @update:content="updatePageContent(page.index, $event)"
            @blur="handleBlur"
            @start-edit="toggleEditPage(page.index)"
          />
        </div>

        <!-- 配图建议框（卡片底部） -->
        <div v-if="getPageImageSuggestion(page)" class="image-suggestion-container">
          <!-- 只读模式 -->
          <div v-if="!isEditingSuggestion(page.index)" class="image-suggestion-box" @dblclick="toggleEditSuggestion(page.index)">
            <div class="suggestion-header">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              <span>{{ getSuggestionLabel(page.type) }}</span>
            </div>
            <div class="suggestion-content">{{ getPageImageSuggestion(page) }}</div>
          </div>

          <!-- 编辑模式 -->
          <div v-else class="image-suggestion-edit-box">
            <div class="suggestion-header">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              <span>{{ getSuggestionLabel(page.type) }}</span>
            </div>
            <textarea
              :value="getEditingSuggestion(page.index)"
              class="suggestion-textarea"
              @input="handleSuggestionInput(page.index, $event)"
              @blur="handleSuggestionBlur(page.index)"
              placeholder="描述想要的配图风格、元素、色调等..."
              rows="3"
            />
          </div>
        </div>

        <div class="word-count">{{ countBodyChars(page.streamingContent || page.content, page.type) }} 字</div>
      </div>

      <!-- 添加按钮卡片（流式中隐藏） -->
      <div
        v-if="!store.isStreaming"
        class="card add-card-dashed"
        @click="addPage('content')"
      >
        <div class="add-content">
          <div class="add-icon">+</div>
          <span>添加页面</span>
        </div>
      </div>
    </div>
    
    <div style="height: 100px;"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'
import ContentRenderer from '../components/ContentRenderer.vue'
import { countBodyChars, parseImageSuggestion, parseTitle, parseCoverTitles } from '../utils/contentParser'

const router = useRouter()
const store = useGeneratorStore()

// 原有状态
const dragOverIndex = ref<number | null>(null)
const draggedIndex = ref<number | null>(null)

// 搜索结果相关状态
const searchResultsExpanded = ref(true)  // 默认展开

// 计算属性：是否应该显示搜索结果
const shouldShowSearchResults = computed(() => {
  return store.usedSearch && store.searchResults.length > 0
})

// 计算属性：展示的搜索结果
const displayedSearchResults = computed(() => {
  if (!store.usedSearch || store.searchResults.length === 0) {
    return []
  }
  return store.searchResults
})

// 打开外部链接
const openLink = (url: string) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

// 新增状态 - 自动保存相关
const saveStatus = ref<{ type: 'saving' | 'saved' | 'error', message: string } | null>(null)
const isSaving = ref(false)
const saveTimer = ref<number | null>(null)
const hasUnsavedChanges = ref(false)

// 编辑状态管理
const editingPageIndex = ref<number | null>(null)

// 配图建议编辑状态（独立的页面索引）
const editingSuggestionPage = ref<number | null>(null)

// 配图建议编辑内容
const editingSuggestions = ref<Record<number, string>>({})

// 编辑时保存的原始完整内容
const originalContentBeforeEdit = ref<string | null>(null)

// 正文编辑时的临时内容
const editingBodyContent = ref<string | null>(null)

const getPageTypeName = (type: string) => {
  const names = {
    cover: '封面',
    content: '内容',
    summary: '总结'
  }
  return names[type as keyof typeof names] || '内容'
}

// 获取页面的配图建议
const getPageImageSuggestion = (page: any) => {
  const content = page.streamingContent || page.content
  const parsed = parseImageSuggestion(content, page.type)
  return parsed.imageSuggestion
}

// 获取页面正文（不含配图建议）
const getPageBodyWithoutSuggestion = (page: any) => {
  const content = page.streamingContent || page.content
  const parsed = parseImageSuggestion(content, page.type)
  return parsed.bodyContent
}

// 获取用于显示的内容（标题 + 正文，不含配图建议）
const getContentForDisplay = (page: any) => {
  // 如果正在编辑正文，返回临时编辑内容
  if (editingPageIndex.value === page.index && editingBodyContent.value !== null) {
    return editingBodyContent.value
  }

  const content = page.streamingContent || page.content

  // 解析配图建议，获取不含配图建议的正文
  const parsed = parseImageSuggestion(content, page.type)
  const bodyContent = parsed.bodyContent

  // 根据页面类型重建内容
  if (page.type === 'cover') {
    // 封面页：主标题 + 副标题 + 正文
    const coverTitles = parseCoverTitles(content)
    let result = ''

    if (coverTitles.mainTitle) {
      const hasKeyword = content.includes('标题：') || content.includes('标题:')
      if (hasKeyword) {
        result = `标题：${coverTitles.mainTitle}\n`
      } else {
        result = `${coverTitles.mainTitle}\n`
      }
    }

    if (coverTitles.subTitle) {
      const hasKeyword = content.includes('副标题：') || content.includes('副标题:')
      if (hasKeyword) {
        result += `副标题：${coverTitles.subTitle}\n`
      } else {
        result += `${coverTitles.subTitle}\n`
      }
    }

    result += bodyContent
    return result
  } else {
    // 其他页面：标题 + 正文
    const title = parseTitle(content, page.type)
    if (title) {
      return `${title}\n${bodyContent}`
    }
    return bodyContent
  }
}

// 判断是否正在编辑配图建议
const isEditingSuggestion = (pageIndex: number) => {
  return editingSuggestionPage.value === pageIndex
}

// 切换配图建议编辑状态
const toggleEditSuggestion = (pageIndex: number) => {
  if (editingSuggestionPage.value === pageIndex) {
    editingSuggestionPage.value = null
  } else {
    editingSuggestionPage.value = pageIndex
  }
}

// 获取配图建议标签（封面显示"背景"，其他显示"配图建议"）
const getSuggestionLabel = (pageType: string) => {
  return pageType === 'cover' ? '背景' : '配图建议'
}

// 获取正在编辑的配图建议内容
const getEditingSuggestion = (pageIndex: number) => {
  const page = store.outline.pages[pageIndex]
  const suggestion = getPageImageSuggestion(page)
  // 如果已经有编辑中的值，使用编辑值；否则使用原始值
  return editingSuggestions.value[pageIndex] ?? suggestion ?? ''
}

// 处理配图建议输入
const handleSuggestionInput = (pageIndex: number, event: Event) => {
  const target = event.target as HTMLTextAreaElement
  editingSuggestions.value[pageIndex] = target.value

  // 实时更新完整内容
  updatePageContentWithSuggestion(pageIndex, target.value)
}

// 处理配图建议失焦
const handleSuggestionBlur = (pageIndex: number) => {
  // 清除编辑状态
  delete editingSuggestions.value[pageIndex]
  editingSuggestionPage.value = null
  // 触发自动保存
  debouncedSave()
}

// 更新页面内容（包含配图建议）
const updatePageContentWithSuggestion = (pageIndex: number, newSuggestion: string) => {
  const page = store.outline.pages[pageIndex]
  const content = page.content || ''

  // 获取不含配图建议的正文
  const parsed = parseImageSuggestion(content, page.type)
  const bodyContent = parsed.bodyContent

  // 构建完整内容
  let fullContent = ''

  // 封面页需要特殊处理（主标题和副标题）
  if (page.type === 'cover') {
    const coverTitles = parseCoverTitles(content)

    if (coverTitles.mainTitle) {
      // 检查原始内容是否使用"标题："关键词
      const hasKeyword = content.includes('标题：') || content.includes('标题:')
      if (hasKeyword) {
        fullContent = `标题：${coverTitles.mainTitle}\n`
      } else {
        fullContent = `${coverTitles.mainTitle}\n`
      }
    }

    if (coverTitles.subTitle) {
      const hasKeyword = content.includes('副标题：') || content.includes('副标题:')
      if (hasKeyword) {
        fullContent += `副标题：${coverTitles.subTitle}\n`
      } else {
        fullContent += `${coverTitles.subTitle}\n`
      }
    }
  } else {
    // 其他页面类型
    const title = parseTitle(content, page.type)
    if (title) {
      fullContent = `${title}\n`
    }
  }

  // 添加正文
  fullContent += bodyContent

  // 添加配图建议/背景
  if (newSuggestion) {
    const label = page.type === 'cover' ? '背景' : '配图建议'
    const separator = fullContent && !fullContent.endsWith('\n') ? '\n' : ''
    fullContent = `${fullContent}${separator}${label}：${newSuggestion}`
  }

  store.updatePage(pageIndex, fullContent)
}

// 防抖保存函数
const debouncedSave = () => {
  if (saveTimer.value) {
    clearTimeout(saveTimer.value)
  }

  saveTimer.value = window.setTimeout(async () => {
    await performAutoSave()
  }, 1000) // 1秒防抖
}

// 执行自动保存
const performAutoSave = async () => {
  if (!hasUnsavedChanges.value) return

  isSaving.value = true
  saveStatus.value = { type: 'saving', message: '正在保存...' }

  try {
    await store.autoSaveDraft()
    saveStatus.value = { type: 'saved', message: '已自动保存' }
    hasUnsavedChanges.value = false

    // 3秒后清除保存状态提示
    setTimeout(() => {
      if (saveStatus.value?.type === 'saved') {
        saveStatus.value = null
      }
    }, 3000)
  } catch (error) {
    console.error('自动保存失败:', error)
    saveStatus.value = { type: 'error', message: '保存失败' }
  } finally {
    isSaving.value = false
  }
}

// 处理输入（已移至 updatePageContent 中，保留此函数用于向后兼容）
const handleInput = () => {
  // 输入处理现在由 updatePageContent 方法处理
  hasUnsavedChanges.value = true
  debouncedSave()
}

// 处理失焦（自动保存并退出编辑）
const handleBlur = () => {
  // 如果正在编辑正文，失焦时需要恢复配图建议
  if (editingPageIndex.value !== null && originalContentBeforeEdit.value) {
    const index = editingPageIndex.value
    const page = store.outline.pages[index]

    // 从原始内容中提取配图建议
    const originalParsed = parseImageSuggestion(originalContentBeforeEdit.value, page.type)

    // 获取编辑后的内容（使用临时内容或原始内容）
    const editedContent = editingBodyContent.value !== null
      ? editingBodyContent.value
      : getContentForDisplay(page)

    // 如果原始内容有配图建议，需要添加回来
    if (originalParsed.imageSuggestion) {
      const label = page.type === 'cover' ? '背景' : '配图建议'
      const separator = editedContent && !editedContent.endsWith('\n') ? '\n' : ''
      const fullContent = `${editedContent}${separator}${label}：${originalParsed.imageSuggestion}`
      store.updatePage(index, fullContent)
    } else {
      // 没有配图建议，直接保存编辑后的内容
      store.updatePage(index, editedContent)
    }
  }

  // 保存更改
  if (hasUnsavedChanges.value) {
    performAutoSave()
  }

  // 退出编辑模式
  stopEditing()
}

// 页面卸载前保存
onMounted(() => {
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
  if (saveTimer.value) {
    clearTimeout(saveTimer.value)
  }
})

// 关闭页面前提醒
const handleBeforeUnload = (e: BeforeUnloadEvent) => {
  if (hasUnsavedChanges.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}

// 拖拽逻辑
const onDragStart = (e: DragEvent, index: number) => {
  draggedIndex.value = index
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.dropEffect = 'move'
  }
}

const onDragOver = (e: DragEvent, index: number) => {
  if (draggedIndex.value === index) return
  dragOverIndex.value = index
}

const onDrop = (e: DragEvent, index: number) => {
  dragOverIndex.value = null
  if (draggedIndex.value !== null && draggedIndex.value !== index) {
    store.movePage(draggedIndex.value, index)
    hasUnsavedChanges.value = true
    debouncedSave()
  }
  draggedIndex.value = null
}

const deletePage = (index: number) => {
  if (confirm('确定要删除这一页吗？')) {
    store.deletePage(index)
    hasUnsavedChanges.value = true
    debouncedSave()
  }
}

const addPage = (type: 'cover' | 'content' | 'summary') => {
  store.addPage(type, '')
  hasUnsavedChanges.value = true
  debouncedSave()
  // 滚动到底部
  nextTick(() => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
  })
}

// 编辑状态管理方法
const toggleEditPage = (pageIndex: number) => {
  if (store.isStreaming) return

  if (editingPageIndex.value === pageIndex) {
    // 如果当前正在编辑此页，退出编辑
    stopEditing()
  } else {
    // 否则进入编辑此页
    editingPageIndex.value = pageIndex
    // 保存原始完整内容
    const page = store.outline.pages[pageIndex]
    originalContentBeforeEdit.value = page.content || ''
    // 初始化临时编辑内容
    editingBodyContent.value = null
  }
}

const stopEditing = () => {
  editingPageIndex.value = null
  originalContentBeforeEdit.value = null
  editingBodyContent.value = null
}

const isEditingPage = (pageIndex: number) => {
  return editingPageIndex.value === pageIndex
}

const updatePageContent = (index: number, content: string) => {
  // 如果正在编辑正文，只更新临时内容，不更新 store
  if (editingPageIndex.value === index) {
    editingBodyContent.value = content
    hasUnsavedChanges.value = true
  } else {
    // 不在编辑状态，直接更新 store
    store.updatePage(index, content)
    hasUnsavedChanges.value = true
    debouncedSave()
  }
}

const goBack = () => {
  router.back()
}

const startGeneration = async () => {
  // 先执行最后一次保存
  if (hasUnsavedChanges.value) {
    await performAutoSave()
  }
  router.push('/generate')
}
</script>

<style scoped>
/* 网格布局 */
.outline-grid {
  display: grid;
  /* 响应式列：最小宽度 320px，自动填充 */
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.outline-card {
  display: flex;
  flex-direction: column;
  padding: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  min-height: 500px;
  position: relative;
  overflow: hidden;
}

.outline-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.06);
  border-color: #d9d9d9;
}

.outline-card.dragging-over {
  border: 2px dashed var(--primary);
  opacity: 0.8;
  background: rgba(255, 36, 66, 0.02);
}

/* 顶部栏 */
.card-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.page-number {
  font-size: 15px;
  font-weight: 600;
  color: #bfbfbf;
  font-family: 'Inter', -apple-system, sans-serif;
  letter-spacing: 0.5px;
}

.page-type {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.page-type.cover {
  color: #ff4d4f;
  background: linear-gradient(135deg, #fff1f0 0%, #ffccc7 100%);
}
.page-type.content {
  color: #595959;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
}
.page-type.summary {
  color: #52c41a;
  background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
}

.card-controls {
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s;
}
.outline-card:hover .card-controls { opacity: 1; }

.drag-handle {
  cursor: grab;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
}
.drag-handle:hover {
  background: #f5f5f5;
}
.drag-handle:active { cursor: grabbing; }

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #8c8c8c;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}
.icon-btn:hover {
  color: #ff4d4f;
  background: #fff1f0;
}

/* 编辑按钮激活状态 */
.card-controls .icon-btn.active {
  color: #1890ff;
  background: #e6f7ff;
}

.card-controls .icon-btn.active:hover {
  color: #40a9ff;
  background: #bae7ff;
}

.word-count {
  text-align: right;
  font-size: 12px;
  color: #bfbfbf;
  margin-top: auto;
  padding-top: 8px;
}

/* 添加卡片 */
.add-card-dashed {
  border: 2px dashed #e8e8e8;
  background: transparent;
  box-shadow: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 320px;
  color: #bfbfbf;
  transition: all 0.3s;
  border-radius: 12px;
}

.add-card-dashed:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.02) 0%, rgba(255, 36, 66, 0.05) 100%);
  transform: translateY(-2px);
}

.add-content {
  text-align: center;
}

.add-icon {
  font-size: 36px;
  font-weight: 200;
  margin-bottom: 10px;
}

/* 新增样式 - 保存状态 */
.save-status {
  font-size: 13px;
  margin-left: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.save-status.saving {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.1);
}

.save-status.saved {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

.save-status.error {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
}

/* 流式进度条 */
.streaming-progress-bar {
  max-width: 1200px;
  margin: 0 auto 24px;
  padding: 12px 20px;
  background: #f5f5f5;
  color: #595959;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid #e8e8e8;
}

/* 卡片状态样式（新增） */
.outline-card.streaming-active {
  border: 1px solid #1890ff;
  box-shadow: none;
}

/* 流式状态徽章（新增） */
.streaming-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
}

.streaming-dot {
  width: 6px;
  height: 6px;
  background: #1890ff;
  border-radius: 50%;
}

/* 内容显示容器 */
.content-display {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 配图建议框（卡片底部） */
.image-suggestion-container {
  margin-top: 12px;
  margin-bottom: 8px;
}

/* 配图建议框（只读） */
.image-suggestion-box {
  padding: 10px 12px;
  background: linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%);
  border: 1px solid #ffd591;
  border-left: 3px solid #fa8c16;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.image-suggestion-box:hover {
  background: linear-gradient(135deg, #ffe7ba 0%, #ffd591 100%);
}

/* 配图建议编辑框 */
.image-suggestion-edit-box {
  padding: 12px;
  background: linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%);
  border: 1px solid #ffd591;
  border-left: 3px solid #fa8c16;
  border-radius: 8px;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  color: #d46b08;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.suggestion-content {
  color: #8c8c8c;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.suggestion-textarea {
  width: 100%;
  min-height: 60px;
  padding: 8px;
  border: 1px solid #ffd591;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.6);
  color: #595959;
  font-size: 12px;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  transition: all 0.2s;
}

.suggestion-textarea:focus {
  outline: none;
  border-color: #fa8c16;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 2px rgba(250, 140, 22, 0.1);
}

/* 控件禁用状态（新增） */
.card-controls.disabled {
  opacity: 0.3;
  pointer-events: none;
}

/* 全局禁用覆盖层（新增） */
.outline-grid.disabled {
  position: relative;
}

.outline-grid.disabled::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.6);
  z-index: 100;
  pointer-events: all;
}

.disabled {
  opacity: 0.5;
  pointer-events: none;
}

/* Spinner 动画 */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid var(--primary, #ff6b6b);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 搜索结果容器样式 - 与卡片风格一致 */
.search-results-container {
  max-width: 1350px;
  margin: 0 auto 24px;
  padding: 0 20px;
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  background: #f9fafb;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  margin: 0 0 12px 0;
  cursor: pointer;
  user-select: none;
}

.search-results-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color, #1f2937);
}

.collapse-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.collapse-toggle-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.search-results-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  margin-bottom: 12px;
}

.search-result-item {
  background: white;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color, #e5e7eb);
  transition: all 0.2s;
}

.search-result-item:hover {
  border-color: var(--primary, #ff6b6b);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 12px;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: #2563eb;
  text-decoration: none;
  line-height: 1.4;
  flex: 1;
}

.result-title:hover {
  text-decoration: underline;
}

.result-source {
  font-size: 11px;
  color: white;
  white-space: nowrap;
  background: var(--primary, #ff6b6b);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.result-snippet {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.6;
}
</style>
