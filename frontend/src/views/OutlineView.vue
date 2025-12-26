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
          <!-- 正在流式：只读显示 + 打字机效果 -->
          <div v-if="page.isStreaming" class="streaming-content">
            <pre class="typewriter-text">
              {{ page.streamingContent }}<span class="cursor">|</span>
            </pre>
          </div>

          <!-- 流式完成或未开始：可编辑文本框 -->
          <textarea
            v-else
            v-model="page.content"
            class="textarea-paper"
            placeholder="在此输入文案..."
            @input="handleInput"
            @blur="handleBlur"
          />
        </div>

        <div class="word-count">{{ (page.streamingContent || page.content).length }} 字</div>
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
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'

const router = useRouter()
const store = useGeneratorStore()

// 原有状态
const dragOverIndex = ref<number | null>(null)
const draggedIndex = ref<number | null>(null)

// 新增状态 - 自动保存相关
const saveStatus = ref<{ type: 'saving' | 'saved' | 'error', message: string } | null>(null)
const isSaving = ref(false)
const saveTimer = ref<number | null>(null)
const hasUnsavedChanges = ref(false)

const getPageTypeName = (type: string) => {
  const names = {
    cover: '封面',
    content: '内容',
    summary: '总结'
  }
  return names[type as keyof typeof names] || '内容'
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

// 处理输入
const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement

  // 由于 v-model="page.content" 已经自动更新了 store.outline.pages 中的内容，
  // 我们只需要触发同步更新 raw 文本即可
  // 这里我们通过检测内容变化来确保 raw 文本同步
  store.syncRawFromPages()

  hasUnsavedChanges.value = true
  // 使用防抖保存
  debouncedSave()
}

// 处理失焦
const handleBlur = () => {
  // 失焦时立即保存（如果有未保存的更改）
  if (hasUnsavedChanges.value) {
    performAutoSave()
  }
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
  font-size: 13px;
  font-weight: 600;
  color: #bfbfbf;
  font-family: 'Inter', -apple-system, sans-serif;
  letter-spacing: 0.5px;
}

.page-type {
  font-size: 11px;
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

/* 文本区域 - 核心 */
.textarea-paper {
  flex: 1;
  width: 100%;
  border: none;
  background: transparent;
  padding: 12px;
  font-size: 15px;
  line-height: 1.8;
  color: #262626;
  resize: none;
  font-family: inherit;
  margin-bottom: 12px;
  border-radius: 6px;
  transition: background 0.2s;
}

.textarea-paper:focus {
  outline: none;
  background: #fafafa;
}

.textarea-paper::placeholder {
  color: #bfbfbf;
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

/* 打字机文本样式（新增） */
.typewriter-text {
  font-family: inherit;
  font-size: 15px;
  line-height: 1.8;
  color: #262626;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.content-display {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.streaming-content {
  flex: 1;
  background: #fafafa;
  border-radius: 6px;
  padding: 12px;
  border: 1px solid #f0f0f0;
}

/* 光标样式 */
.cursor {
  display: inline-block;
  animation: blink 1s step-end infinite;
  color: #1890ff;
  font-weight: 600;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
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
</style>
