<template>
  <div class="container unified-width">
    <div class="page-header glass-header">
      <div>
        <h1 class="page-title gradient-title">编辑大纲</h1>
        <p class="page-subtitle">
          调整页面顺序，修改文案，打造完美内容
          <span v-if="saveStatus" class="save-status" :class="saveStatus.type">
            {{ saveStatus.message }}
          </span>
        </p>
      </div>
      <div style="display: flex; gap: 12px;">
        <button
          class="btn btn-secondary btn-hover-enhanced"
          @click="goBack"
          :disabled="store.isStreaming || store.isCopywritingStreaming"
          style="background: white; border: 1px solid var(--border-color);"
        >
          上一步
        </button>

        <!-- 生成文案按钮（可选） -->
        <button
          class="btn btn-primary btn-hover-enhanced"
          @click="generateCopywriting"
          :disabled="store.isStreaming || store.isCopywritingStreaming"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px;">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
          {{ store.isCopywritingStreaming ? '生成中...' : '生成文案' }}
        </button>

        <!-- 开始生成图片按钮（可直接生成） -->
        <button
          class="btn btn-success btn-hover-enhanced"
          @click="startGeneration"
          :disabled="isSaving || store.isStreaming || store.isCopywritingStreaming"
          style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;">
            <path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path>
            <line x1="16" y1="8" x2="2" y2="22"></line>
            <line x1="17.5" y1="15" x2="9" y2="15"></line>
          </svg>
          {{ isSaving ? '保存中...' : '开始生成图片' }}
        </button>
      </div>
    </div>

    <!-- 流式生成进度提示（修改） -->
    <div v-if="store.isStreaming" class="streaming-progress-bar unified-width">
      <div class="spinner"></div>
      <span>AI 正在创作中... ({{ store.outline.pages.length }} 页)</span>
    </div>

    <!-- 文案生成进度提示（新增） -->
    <div v-if="store.isCopywritingStreaming" class="streaming-progress-bar unified-width" style="background: linear-gradient(135deg, #E6F7FF 0%, #BAE7FF 100%); border: 1px solid rgba(24, 144, 255, 0.2);">
      <div class="spinner" style="border-color: #1890FF transparent #1890FF transparent;"></div>
      <span style="color: #1890FF;">AI 正在创作文案...</span>
      <span class="loading-dots">
        <span>.</span><span>.</span><span>.</span>
      </span>
    </div>

    <!-- 搜索结果展示区域 -->
    <div
      v-if="shouldShowSearchResults"
      class="search-results-container unified-width"
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
          <div class="result-snippet" :title="result.snippet">{{ result.snippet }}</div>
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

    <!-- 文案卡片（新增） -->
    <CopywritingCard
      v-if="store.copywriting.title || store.isCopywritingStreaming"
      :copywriting="store.copywriting"
      :is-streaming="store.isCopywritingStreaming"
      :accumulated-text="store.copywritingAccumulatedText"
      @update:copywriting="handleCopywritingUpdate"
      @regenerate="generateCopywriting"
      class="unified-width"
      style="margin-bottom: var(--space-6);"
    />

    <div style="height: 100px;"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'
import ContentRenderer from '../components/ContentRenderer.vue'
import CopywritingCard from '../components/CopywritingCard.vue'
import { countBodyChars, parseImageSuggestion, parseTitle, parseCoverTitles } from '../utils/contentParser'
import { generateCopywritingStream } from '../api'

const router = useRouter()
const store = useGeneratorStore()

// 原有状态
const dragOverIndex = ref<number | null>(null)
const draggedIndex = ref<number | null>(null)

// 搜索结果相关状态
const searchResultsExpanded = ref(false)  // 默认收起，搜索时自动展开

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

// 监听搜索状态，自动控制展开/收起
watch(() => store.isStreaming, (isStreaming, wasStreaming) => {
  // 当开始流式生成时，如果有搜索结果则展开
  if (isStreaming && store.usedSearch && store.searchResults.length > 0) {
    searchResultsExpanded.value = true
  }
  // 当流式生成完成时，自动收起
  if (!isStreaming && wasStreaming) {
    searchResultsExpanded.value = false
  }
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

  // 标记为有未保存的更改
  hasUnsavedChanges.value = true

  // 实时更新完整内容
  updatePageContentWithSuggestion(pageIndex, target.value)
}

// 处理配图建议失焦
const handleSuggestionBlur = (pageIndex: number) => {
  // 确保内容已保存
  const suggestion = editingSuggestions.value[pageIndex]
  if (suggestion !== undefined) {
    updatePageContentWithSuggestion(pageIndex, suggestion)
  }

  // 清除编辑状态
  delete editingSuggestions.value[pageIndex]
  editingSuggestionPage.value = null

  // 触发自动保存（1秒防抖）
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

// ========== 文案生成相关 ==========

// 生成文案
const generateCopywriting = async () => {
  // 确保大纲已保存
  if (!store.outline.raw || store.outline.pages.length === 0) {
    alert('请先生成大纲')
    return
  }

  store.startCopywritingStreaming()

  try {
    await generateCopywritingStream(
      store.topic,
      store.outline,
      // onText
      (chunk, accumulated) => {
        store.updateCopywritingStreaming(chunk, accumulated)
      },
      // onComplete
      (result) => {
        store.finishCopywritingStreaming(result)
        console.log('文案生成完成:', result)

        // 自动滚动到文案卡片并添加高亮动画
        setTimeout(() => {
          const card = document.querySelector('.copywriting-card')
          if (card) {
            // 平滑滚动到卡片位置
            card.scrollIntoView({ behavior: 'smooth', block: 'center' })

            // 添加高亮动画
            card.classList.add('just-generated')
            setTimeout(() => card.classList.remove('just-generated'), 1500)
          }
        }, 500)
      },
      // onError
      (error) => {
        console.error('文案生成失败:', error)
        store.stopCopywritingStreaming()
        alert('文案生成失败：' + error)
      }
    )
  } catch (error) {
    console.error('文案生成异常:', error)
    store.stopCopywritingStreaming()
    alert('文案生成异常，请重试')
  }
}

// 更新文案
const handleCopywritingUpdate = (data: any) => {
  store.updateCopywriting(data)
}

// ========== 原有逻辑 ==========

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
/* 统一宽度和对齐 */
.unified-width {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

/* 加载动画点 */
.loading-dots {
  display: inline-flex;
  gap: 4px;
  margin-left: 8px;
}

.loading-dots span {
  animation: blink 1.4s infinite;
  font-size: 20px;
  line-height: 1;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%, 100% {
    opacity: 0.2;
  }
  50% {
    opacity: 1;
  }
}

/* 玻璃态头部样式 */
.glass-header {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: var(--space-6) var(--space-8);
  box-shadow: var(--glass-shadow);
  transition: all var(--duration-slow) var(--ease-out);
  margin-bottom: var(--space-8);
}

/* 渐变标题 */
.gradient-title {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 网格布局 - 统一间距 */
.outline-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--space-6);
}

.outline-card {
  display: flex;
  flex-direction: column;
  padding: var(--space-4);
  transition: all var(--duration-slow) var(--ease-out);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-lg);
  background: var(--gradient-card);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow:
    var(--shadow-sm),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  min-height: 500px;
  position: relative;
  overflow: hidden;
  /* 硬件加速 */
  will-change: transform, box-shadow;
  transform: translateZ(0);
}

.outline-card:hover {
  transform: translateY(-4px) translateZ(0);
  box-shadow:
    var(--shadow-primary),
    0 0 0 1px rgba(255, 36, 66, 0.1) inset;
  border-color: rgba(255, 36, 66, 0.2);
}

.outline-card.dragging-over {
  border: 2px dashed var(--primary);
  background: rgba(255, 36, 66, 0.03);
  box-shadow: 0 0 0 4px rgba(255, 36, 66, 0.1);
  animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 0 4px rgba(255, 36, 66, 0.1); }
  50% { box-shadow: 0 0 0 8px rgba(255, 36, 66, 0.05); }
}

/* 顶部栏 - 统一间距 */
.card-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border-color);
}

.page-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.page-number {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  font-family: 'Inter', -apple-system, sans-serif;
  letter-spacing: 0.5px;
}

.page-type {
  font-size: 11px;
  padding: 5px 12px;
  border-radius: 8px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  backdrop-filter: blur(5px);
}
.page-type.cover {
  color: #D91C36;
  background: linear-gradient(135deg, #FFF0F2 0%, #FFD4D9 100%);
  border: 1px solid rgba(217, 28, 54, 0.2);
}
.page-type.content {
  color: #4A4A4A;
  background: linear-gradient(135deg, #F5F5F5 0%, #E8E8E8 100%);
  border: 1px solid rgba(0, 0, 0, 0.1);
}
.page-type.summary {
  color: #389E0D;
  background: linear-gradient(135deg, #F6FFED 0%, #D9F7BE 100%);
  border: 1px solid rgba(82, 196, 26, 0.2);
}

.card-controls {
  display: flex;
  gap: var(--space-2);
  opacity: 0;
  transition: opacity var(--duration-normal) var(--ease-out);
}
.outline-card:hover .card-controls { opacity: 1; }

.drag-handle {
  cursor: grab;
  padding: var(--space-2);
  border-radius: var(--radius-xs);
  transition: all var(--duration-normal) var(--ease-out);
}
.drag-handle:hover {
  background: rgba(0, 0, 0, 0.05);
  transform: scale(1.1);
}
.drag-handle:active {
  cursor: grabbing;
  transform: scale(0.95);
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  padding: var(--space-1);
  border-radius: var(--radius-xs);
  transition: all var(--duration-normal) var(--ease-out);
}
.icon-btn:hover {
  transform: scale(1.1);
  color: var(--primary);
  background: rgba(255, 36, 66, 0.1);
}

.icon-btn:active {
  transform: scale(0.95);
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
  color: var(--text-secondary);
  margin-top: auto;
  padding-top: var(--space-2);
}

/* 添加卡片 - 统一样式 */
.add-card-dashed {
  border: 2px dashed rgba(255, 36, 66, 0.3);
  background: linear-gradient(
    135deg,
    rgba(255, 36, 66, 0.02) 0%,
    rgba(255, 36, 66, 0.05) 100%
  );
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 320px;
  color: var(--primary);
  transition: all var(--duration-slow) var(--ease-out);
  /* 硬件加速 */
  will-change: transform, box-shadow;
  transform: translateZ(0);
}

.add-card-dashed:hover {
  border-color: var(--primary);
  border-style: solid;
  background: linear-gradient(
    135deg,
    rgba(255, 36, 66, 0.05) 0%,
    rgba(255, 36, 66, 0.1) 100%
  );
  transform: translateY(-4px) scale(1.02) translateZ(0);
  box-shadow: var(--shadow-primary);
}

.add-content {
  text-align: center;
}

.add-icon {
  font-size: 48px;
  font-weight: 200;
  color: var(--primary);
  opacity: 0.8;
  transition: all var(--duration-slow) var(--ease-out);
  margin-bottom: var(--space-3);
}

.add-card-dashed:hover .add-icon {
  transform: rotate(90deg);
  opacity: 1;
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

/* 流式进度条 - 统一样式 */
.streaming-progress-bar {
  padding: var(--space-3) var(--space-5);
  background: rgba(249, 250, 251, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: var(--text-sub);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: 14px;
  font-weight: 500;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-xs);
  margin-bottom: var(--space-6);
}

/* 卡片状态样式（新增） */
.outline-card.streaming-active {
  border: 1px solid var(--info);
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
  position: relative;
  overflow: hidden;
}

/* 流式光效背景 */
.outline-card.streaming-active::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(24, 144, 255, 0.1),
    transparent
  );
  animation: shimmer 2s infinite;
  pointer-events: none;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* 流式状态徽章（新增） */
.streaming-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(24, 144, 255, 0.1);
  color: var(--info);
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid rgba(24, 144, 255, 0.2);
  backdrop-filter: blur(5px);
}

.streaming-dot {
  width: 6px;
  height: 6px;
  background: var(--info);
  border-radius: 50%;
  animation: pulse-dot 1.5s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.7;
  }
}

/* 内容显示容器 - 增强层次 */
.content-display {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: var(--space-3) 0;
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-md);
  /* 性能优化 */
  contain: layout style paint;
}

/* 配图建议框（卡片底部） */
.image-suggestion-container {
  margin-top: var(--space-3);
  margin-bottom: var(--space-2);
}

/* 配图建议框 - 统一间距和动画 */
.image-suggestion-box {
  padding: var(--space-3) var(--space-4);
  background: linear-gradient(
    135deg,
    rgba(255, 247, 230, 0.8) 0%,
    rgba(255, 231, 186, 0.6) 100%
  );
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(250, 140, 22, 0.3);
  border-left: 3px solid var(--warning);
  border-radius: var(--radius-md);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--duration-slow) var(--ease-out);
}

.image-suggestion-box:hover {
  background: linear-gradient(
    135deg,
    rgba(255, 231, 186, 0.9) 0%,
    rgba(255, 213, 145, 0.8) 100%
  );
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(250, 140, 22, 0.15);
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

/* 按钮悬停增强效果 */
.btn-hover-enhanced {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary.btn-hover-enhanced:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 36, 66, 0.25);
}

.btn-secondary.btn-hover-enhanced:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(255, 36, 66, 0.05);
  transform: translateY(-2px);
}

/* 搜索结果容器 - 统一样式 */
.search-results-container {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--glass-shadow);
  overflow: hidden;
  transition: all var(--duration-slow) var(--ease-out);
  margin-bottom: var(--space-6);
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  background: rgba(249, 250, 251, 0.5);
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  cursor: pointer;
  user-select: none;
  transition: background var(--duration-normal) var(--ease-out);
}

.search-results-header:hover {
  background: rgba(249, 250, 251, 0.8);
}

.search-results-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.collapse-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xs);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
  flex-shrink: 0;
}

.collapse-toggle-btn:hover {
  background: #f9fafb;
  border-color: var(--border-hover);
}

.search-results-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-3);
  padding: 0 var(--space-5) var(--space-5) var(--space-5);
}

.search-result-item {
  background: rgba(255, 255, 255, 0.6);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid rgba(229, 231, 235, 0.5);
  transition: all var(--duration-slow) var(--ease-out);
}

.search-result-item:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 36, 66, 0.3);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
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
  /* 限制最多显示 2 行，超出部分显示省略号 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 辅助功能：减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 焦点状态优化（键盘导航） */
button:focus-visible,
.icon-btn:focus-visible,
.collapse-toggle-btn:focus-visible,
.add-card-dashed:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* 响应式优化 - 统一断点 */
@media (max-width: 1024px) {
  .unified-width {
    padding: 0 var(--space-5);
  }

  .outline-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--space-5);
  }

  .glass-header {
    padding: var(--space-5) var(--space-6);
  }
}

@media (max-width: 768px) {
  .unified-width {
    padding: 0 var(--space-4);
  }

  .outline-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }

  .glass-header {
    padding: var(--space-4);
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }
}

@media (max-width: 640px) {
  .unified-width {
    padding: 0 var(--space-3);
  }

  .glass-header {
    border-radius: var(--radius-md);
    padding: var(--space-4);
  }

  .page-title {
    font-size: 28px;
  }

  .search-results-list {
    grid-template-columns: 1fr;
  }
}
</style>
