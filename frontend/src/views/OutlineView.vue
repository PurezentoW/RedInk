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
        <button class="btn btn-secondary" @click="goBack" style="background: white; border: 1px solid var(--border-color);">
          上一步
        </button>
        <button
          class="btn btn-primary"
          @click="startGeneration"
          :disabled="isSaving"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path><line x1="16" y1="8" x2="2" y2="22"></line><line x1="17.5" y1="15" x2="9" y2="15"></line></svg>
          {{ isSaving ? '保存中...' : '开始生成图片' }}
        </button>
      </div>
    </div>

    <div class="outline-grid">
      <div 
        v-for="(page, idx) in store.outline.pages" 
        :key="page.index"
        class="card outline-card"
        :draggable="true"
        @dragstart="onDragStart($event, idx)"
        @dragover.prevent="onDragOver($event, idx)"
        @drop="onDrop($event, idx)"
        :class="{ 'dragging-over': dragOverIndex === idx }"
      >
        <!-- 拖拽手柄 (改为右上角或更加隐蔽) -->
        <div class="card-top-bar">
          <div class="page-info">
             <span class="page-number">P{{ idx + 1 }}</span>
             <span class="page-type" :class="page.type">{{ getPageTypeName(page.type) }}</span>
          </div>
          
          <div class="card-controls">
            <div class="drag-handle" title="拖拽排序">
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="1"></circle><circle cx="9" cy="5" r="1"></circle><circle cx="9" cy="19" r="1"></circle><circle cx="15" cy="12" r="1"></circle><circle cx="15" cy="5" r="1"></circle><circle cx="15" cy="19" r="1"></circle></svg>
            </div>
            <button class="icon-btn" @click="deletePage(idx)" title="删除此页">
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
        </div>

        <textarea
          v-model="page.content"
          class="textarea-paper"
          placeholder="在此输入文案..."
          @input="handleInput"
          @blur="handleBlur"
        />
        
        <div class="word-count">{{ page.content.length }} 字</div>
      </div>

      <!-- 添加按钮卡片 -->
      <div class="card add-card-dashed" @click="addPage('content')">
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
  /* 响应式列：最小宽度 280px，自动填充 */
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.outline-card {
  display: flex;
  flex-direction: column;
  padding: 16px; /* 减小内边距 */
  transition: all 0.2s ease;
  border: none;
  border-radius: 8px; /* 较小的圆角 */
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  /* 保持一定的长宽比感，虽然高度自适应，但由于 flex column 和内容撑开，
     这里设置一个 min-height 让它看起来像个竖向卡片 */
  min-height: 360px; 
  position: relative;
}

.outline-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  z-index: 10;
}

.outline-card.dragging-over {
  border: 2px dashed var(--primary);
  opacity: 0.8;
}

/* 顶部栏 */
.card-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f5f5f5;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-number {
  font-size: 14px;
  font-weight: 700;
  color: #ccc;
  font-family: 'Inter', sans-serif;
}

.page-type {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.page-type.cover { color: #FF4D4F; background: #FFF1F0; }
.page-type.content { color: #8c8c8c; background: #f5f5f5; }
.page-type.summary { color: #52C41A; background: #F6FFED; }

.card-controls {
  display: flex;
  gap: 8px;
  opacity: 0.4;
  transition: opacity 0.2s;
}
.outline-card:hover .card-controls { opacity: 1; }

.drag-handle {
  cursor: grab;
  padding: 2px;
}
.drag-handle:active { cursor: grabbing; }

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 2px;
  transition: color 0.2s;
}
.icon-btn:hover { color: #FF4D4F; }

/* 文本区域 - 核心 */
.textarea-paper {
  flex: 1; /* 占据剩余空间 */
  width: 100%;
  border: none;
  background: transparent;
  padding: 0;
  font-size: 16px; /* 更大的字号 */
  line-height: 1.7; /* 舒适行高 */
  color: #333;
  resize: none; /* 禁止手动拉伸，保持卡片整体感 */
  font-family: inherit;
  margin-bottom: 10px;
}

.textarea-paper:focus {
  outline: none;
}

.word-count {
  text-align: right;
  font-size: 11px;
  color: #ddd;
  margin-top: auto;
}

/* 添加卡片 */
.add-card-dashed {
  border: 2px dashed #eee;
  background: transparent;
  box-shadow: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 360px;
  color: #ccc;
  transition: all 0.2s;
}

.add-card-dashed:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(255, 36, 66, 0.02);
}

.add-content {
  text-align: center;
}

.add-icon {
  font-size: 32px;
  font-weight: 300;
  margin-bottom: 8px;
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
</style>
