<template>
  <div class="card copywriting-card">
    <!-- 顶部栏 -->
    <div class="card-top-bar">
      <div class="page-info">
        <span class="page-type copywriting-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px;">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
          文案
        </span>
        <span v-if="isStreaming" class="streaming-badge">
          <span class="streaming-dot"></span>
          生成中
        </span>
      </div>

      <div class="card-controls" :class="{ disabled: isStreaming }">
        <button
          class="icon-btn"
          @click="regenerate"
          title="重新生成"
          :disabled="isStreaming"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
        </button>
        <button
          class="icon-btn"
          @click="copyAll"
          title="一键复制"
          :disabled="isStreaming"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- 标题区域 -->
    <div class="content-section">
      <div class="section-label">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px;">
          <path d="M12 20h9"></path>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
        </svg>
        笔记标题
      </div>
      <textarea
        v-if="isEditingTitle"
        ref="titleTextarea"
        v-model="editingTitle"
        class="editable-textarea"
        @blur="finishEditTitle"
        @keydown.enter.prevent="finishEditTitle"
        placeholder="输入吸引人的标题..."
      />
      <div
        v-else
        class="display-content title-display"
        @dblclick="startEditTitle"
      >
        {{ displayTitle || '点击生成文案...' }}
      </div>
    </div>

    <!-- 正文区域 - 支持多段显示 -->
    <div class="content-section">
      <div class="section-label">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px;">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"></path>
          <line x1="16" y1="8" x2="8" y2="8"></line>
          <line x1="16" y1="16" x2="8" y2="16"></line>
          <line x1="10" y1="12" x2="8" y2="12"></line>
        </svg>
        正文介绍
      </div>
      <textarea
        v-if="isEditingContent"
        v-model="editingContent"
        class="editable-textarea"
        @blur="finishEditContent"
        placeholder="输入简洁有趣的介绍..."
        rows="8"
      />
      <div
        v-else
        class="display-content content-display"
        @dblclick="startEditContent"
      >
        <!-- 支持多段正文显示 -->
        <div v-if="displayContent" class="content-paragraphs">
          <p
            v-for="(paragraph, index) in contentParagraphs"
            :key="index"
            class="content-paragraph"
          >
            {{ paragraph }}
          </p>
        </div>
        <span v-else class="content-placeholder">...</span>
      </div>
    </div>

    <!-- 标签区域 -->
    <div class="content-section">
      <div class="section-label">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px;">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
          <line x1="7" y1="7" x2="7.01" y2="7"></line>
        </svg>
        话题标签
      </div>
      <div class="tags-display">
        <span
          v-for="(tag, index) in displayTags"
          :key="index"
          class="tag-chip"
        >
          #{{ tag }}
        </span>
        <span v-if="displayTags.length === 0" class="tags-empty">
          暂无标签
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'

interface CopywritingData {
  raw: string
  title: string
  content: string
  tags: string[]
}

interface Props {
  copywriting: CopywritingData
  isStreaming: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:copywriting': [value: CopywritingData]
  'regenerate': []
}>()

// 编辑状态
const isEditingTitle = ref(false)
const isEditingContent = ref(false)
const editingTitle = ref('')
const editingContent = ref('')
const titleTextarea = ref<HTMLTextAreaElement | null>(null)

// 计算属性
const displayTitle = computed(() => props.copywriting?.title || '')
const displayContent = computed(() => props.copywriting?.content || '')
const displayTags = computed(() => props.copywriting?.tags || [])

// 将正文按段落分割（支持多个段落）
const contentParagraphs = computed(() => {
  if (!displayContent.value) return []
  // 按换行符分割，过滤空段落
  return displayContent.value
    .split(/\n\n+/)
    .map(p => p.trim())
    .filter(p => p.length > 0)
})

// 方法
const startEditTitle = () => {
  if (props.isStreaming) return
  editingTitle.value = displayTitle.value
  isEditingTitle.value = true
  nextTick(() => titleTextarea.value?.focus())
}

const finishEditTitle = () => {
  isEditingTitle.value = false
  if (editingTitle.value !== displayTitle.value) {
    emit('update:copywriting', {
      ...props.copywriting,
      title: editingTitle.value
    })
  }
}

const startEditContent = () => {
  if (props.isStreaming) return
  // 保持原始格式，包含换行符
  editingContent.value = displayContent.value
  isEditingContent.value = true
}

const finishEditContent = () => {
  isEditingContent.value = false
  if (editingContent.value !== displayContent.value) {
    emit('update:copywriting', {
      ...props.copywriting,
      content: editingContent.value
    })
  }
}

const regenerate = () => {
  emit('regenerate')
}

const copyAll = async () => {
  const text = `${displayTitle.value}\n\n${displayContent.value}\n\n${displayTags.value.map(t => '#' + t).join(' ')}`

  try {
    await navigator.clipboard.writeText(text)
    showCopySuccess()
  } catch (error) {
    // 降级处理
    const textarea = document.createElement('textarea')
    textarea.value = text
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    showCopySuccess()
  }
}

const showCopySuccess = () => {
  const toast = document.createElement('div')
  toast.className = 'copy-success-toast'
  toast.textContent = '✓ 已复制到剪贴板'
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 12px 24px;
    border-radius: 50px;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    z-index: 9999;
    transition: opacity 0.3s;
    font-weight: 600;
    font-size: 14px;
  `
  document.body.appendChild(toast)

  setTimeout(() => {
    toast.style.opacity = '0'
    setTimeout(() => document.body.removeChild(toast), 300)
  }, 2000)
}
</script>

<style scoped>
.copywriting-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 240, 242, 0.5) 100%);
  border: 1px solid rgba(255, 36, 66, 0.1);
  border-radius: var(--radius-xl, 24px);
  padding: 32px;
  padding-top: 40px; /* 顶部留出空间给红线 */
  box-shadow: var(--shadow-sm);
  margin-bottom: 24px;
  position: relative;
  overflow: hidden; /* 确保红线不超出卡片 */
  /* 禁用全局 card 的 hover 效果 */
  transform: none !important;
}

/* 禁用全局 card:hover 的 transform */
.copywriting-card:hover {
  transform: none !important;
  box-shadow: var(--shadow-md);
}

.copywriting-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px; /* 增加红线高度 */
  background: linear-gradient(90deg, #FF2442 0%, #FF6B8A 50%, #FF2442 100%);
  border-radius: var(--radius-xl, 24px) var(--radius-xl, 24px) 0 0;
  z-index: 0; /* 在最底层 */
}

/* 顶部栏 */
.card-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px; /* 向下移动，避免与红线重叠 */
  margin-bottom: 24px;
  position: relative;
  z-index: 1; /* 确保在红线上方 */
}

.page-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.copywriting-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  background: linear-gradient(135deg, #E6F7FF 0%, #BAE7FF 100%);
  color: #1890FF;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(24, 144, 255, 0.2);
}

.streaming-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background: linear-gradient(135deg, #FFF0F2 0%, #FFD4D9 100%);
  color: #FF2442;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  animation: pulse 2s ease-in-out infinite;
}

.streaming-dot {
  width: 8px;
  height: 8px;
  background: #FF2442;
  border-radius: 50%;
  margin-right: 6px;
  animation: blink 1.5s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

/* 控制按钮 */
.card-controls {
  display: flex;
  gap: 8px;
}

.card-controls.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--text-sub);
}

.icon-btn:hover:not(:disabled) {
  background: #FFF0F2;
  border-color: rgba(255, 36, 66, 0.2);
  color: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(255, 36, 66, 0.15);
}

.icon-btn:active:not(:disabled) {
  transform: translateY(0);
}

.icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 内容区域 */
.content-section {
  margin-bottom: 20px;
}

.section-label {
  display: flex;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-sub);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.display-content {
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.display-content:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 36, 66, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.title-display {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1.4;
}

.content-display {
  font-size: 14px;
  color: var(--text-main);
  line-height: 1.8;
}

/* 多段正文容器 */
.content-paragraphs {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-paragraph {
  margin: 0;
  padding: 0;
  line-height: 1.8;
}

.content-paragraph:not(:last-child)::after {
  content: '';
  display: block;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(0, 0, 0, 0.06) 50%, transparent 100%);
  margin-top: 8px;
}

.content-placeholder {
  color: var(--text-secondary);
  font-style: italic;
}

.editable-textarea {
  width: 100%;
  padding: 16px 20px;
  background: white;
  border: 2px solid var(--primary);
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.8;
  resize: vertical;
  font-family: inherit;
  transition: all 0.2s;
}

.editable-textarea:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.1);
}

/* 标签区域 */
.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.04);
  border-radius: 12px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  background: linear-gradient(135deg, #FFF0F2 0%, #FFD4D9 100%);
  color: #D91C36;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(217, 28, 54, 0.1);
  transition: all 0.2s;
}

.tag-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(217, 28, 54, 0.15);
}

.tags-empty {
  color: var(--text-secondary);
  font-size: 13px;
  font-style: italic;
}
</style>
