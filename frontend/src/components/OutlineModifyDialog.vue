<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modify-dialog-overlay" @click.self="handleClose">
      <div class="modify-dialog">
        <!-- 头部 -->
        <div class="dialog-header">
          <h3>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
              <path d="M2 17l10 5 10-5"></path>
              <path d="M2 12l10 5 10-5"></path>
            </svg>
            AI修改大纲
          </h3>
          <button @click="handleClose" class="close-btn">✕</button>
        </div>

        <!-- 输入区域 -->
        <div class="dialog-input">
          <textarea
            v-model="instruction"
            placeholder="输入修改指令，例如：&#10;• 页数太多了，缩短到3页&#10;• 内容太简单了，增加一些细节&#10;• 改成更专业的语气"
            rows="4"
            :disabled="isModifying"
            class="instruction-textarea"
          />

          <!-- 快捷指令按钮 -->
          <div class="quick-commands">
            <button
              v-for="cmd in quickCommands"
              :key="cmd.label"
              @click="applyQuickCommand(cmd.text)"
              :disabled="isModifying"
              class="quick-command-btn"
            >
              {{ cmd.label }}
            </button>
          </div>
        </div>

        <!-- 侧边预览区域 -->
        <div v-if="isModifying || modifiedPages.length > 0" class="preview-container">
          <!-- 左侧：原大纲摘要 -->
          <div class="original-outline">
            <h4>当前大纲 ({{ originalPages.length }}页)</h4>
            <div class="page-list">
              <div v-for="(page, idx) in originalPages" :key="idx" class="page-item">
                P{{ idx + 1 }} · {{ getPageTypeName(page.type) }}
              </div>
            </div>
          </div>

          <!-- 右侧：修改预览 -->
          <div class="modified-preview">
            <h4>修改后大纲 ({{ modifiedPages.length }}页)</h4>
            <div v-if="isModifying" class="preview-loading">
              <div class="spinner"></div>
              <span>AI正在修改中...</span>
            </div>
            <div v-else class="preview-cards">
              <div
                v-for="(page, idx) in modifiedPages"
                :key="idx"
                class="preview-card"
              >
                <div class="card-label">
                  P{{ idx + 1 }} · {{ getPageTypeName(page.type) }}
                </div>
                <div class="card-content">
                  {{ page.content.substring(0, 100) }}{{ page.content.length > 100 ? '...' : '' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 完成后的操作区 -->
        <div v-if="modifyResult" class="dialog-actions">
          <div class="modify-summary">
            ✨ {{ modifyResult.summary }}
          </div>

          <div class="action-buttons">
            <button @click="handleCancel" class="btn-secondary">
              取消
            </button>
            <button @click="handleApply" class="btn-primary">
              应用修改
            </button>
          </div>
        </div>

        <!-- 底部按钮（修改前） -->
        <div v-else class="dialog-footer">
          <button
            @click="startModify"
            :disabled="!instruction.trim() || isModifying"
            class="btn-primary"
          >
            {{ isModifying ? '修改中...' : '开始修改' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { modifyOutlineStream } from '../api'

interface Page {
  index: number
  type: 'cover' | 'content' | 'summary'
  content: string
}

interface Props {
  isOpen: boolean
  originalOutline: {
    raw: string
    pages: Page[]
  }
}

interface Emits {
  (e: 'close'): void
  (e: 'apply', result: { outline: string; pages: Page[]; summary: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 状态
const instruction = ref('')
const isModifying = ref(false)
const modifiedPages = ref<Page[]>([])
const modifyResult = ref<{ outline: string; pages: Page[]; summary: string } | null>(null)

// 快捷指令
const quickCommands = [
  { label: "缩短页数", text: "页数太多了，请精简到3-5页，保留核心内容" },
  { label: "增加细节", text: "内容太简单了，请增加更多细节和实用信息" },
  { label: "更专业", text: "请用更专业的语气重新组织内容" },
  { label: "更口语化", text: "请用更轻松、口语化的方式表达" },
  { label: "添加总结", text: "请在最后添加一个总结页" },
  { label: "调整语气", text: "请把语气调整得更友好亲切一些" }
]

// 计算属性
const originalPages = computed(() => props.originalOutline?.pages || [])

// 方法
const getPageTypeName = (type: string) => {
  const names = {
    cover: '封面',
    content: '内容',
    summary: '总结'
  }
  return names[type as keyof typeof names] || '内容'
}

const applyQuickCommand = (text: string) => {
  instruction.value = text
}

const handleClose = () => {
  if (isModifying.value) {
    if (!confirm('修改正在进行中，确定要关闭吗？')) {
      return
    }
  }
  reset()
  emit('close')
}

const reset = () => {
  instruction.value = ''
  isModifying.value = false
  modifiedPages.value = []
  modifyResult.value = null
}

const startModify = async () => {
  if (!instruction.value.trim()) {
    return
  }

  isModifying.value = true
  modifiedPages.value = []
  modifyResult.value = null

  try {
    await modifyOutlineStream(
      props.originalOutline.raw || '',
      props.originalOutline,
      instruction.value,
      // onText
      (chunk: string, accumulated: string) => {
        // 简单解析页面（按 <page> 分割）
        const pages = accumulated.split(/<page>/i).filter((p: string) => p.trim())
        modifiedPages.value = pages.map((content: string, index: number) => {
          let type = 'content'
          const typeMatch = content.match(/^\[(\S+)\]/)
          if (typeMatch) {
            const typeMap: Record<string, string> = {
              '封面': 'cover',
              '内容': 'content',
              '总结': 'summary'
            }
            type = typeMap[typeMatch[1]] || 'content'
          }
          return {
            index,
            type: type as 'cover' | 'content' | 'summary',
            content: content.trim()
          }
        })
      },
      // onComplete
      (result: { outline: string; pages: Page[]; summary: string }) => {
        modifyResult.value = result
        modifiedPages.value = result.pages
        isModifying.value = false
      },
      // onError
      (error: string) => {
        console.error('修改失败:', error)
        alert('修改失败：' + error)
        isModifying.value = false
      }
    )
  } catch (error: any) {
    console.error('修改异常:', error)
    alert('修改异常：' + error.message)
    isModifying.value = false
  }
}

const handleCancel = () => {
  reset()
  emit('close')
}

const handleApply = () => {
  if (modifyResult.value) {
    emit('apply', modifyResult.value)
    reset()
    emit('close')
  }
}

// 监听对话框关闭
watch(() => props.isOpen, (newVal) => {
  if (!newVal) {
    reset()
  }
})
</script>

<style scoped>
.modify-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modify-dialog {
  background: var(--glass-bg, rgba(255, 255, 255, 0.7));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.3));
  border-radius: 16px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: dialog-enter 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes dialog-enter {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #E5E7EB);
}

.dialog-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main, #1F2937);
}

.dialog-header h3 svg {
  color: var(--primary, #FF2442);
}

.close-btn {
  background: transparent;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #9CA3AF);
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-main, #1F2937);
  transform: rotate(90deg);
}

.dialog-input {
  padding: 24px;
}

.instruction-textarea {
  width: 100%;
  padding: 16px;
  border: 1px solid var(--border-color, #E5E7EB);
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  background: rgba(255, 255, 255, 0.5);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.instruction-textarea:focus {
  outline: none;
  background: #FFFFFF;
  border-color: var(--primary, #FF2442);
  box-shadow: 0 0 0 4px rgba(255, 36, 66, 0.1);
}

.instruction-textarea:disabled {
  background: rgba(0, 0, 0, 0.02);
  color: var(--text-secondary, #9CA3AF);
}

.quick-commands {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.quick-command-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #FF2442 0%, #FF6B8A 100%);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(255, 36, 66, 0.2);
}

.quick-command-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.35);
}

.quick-command-btn:active:not(:disabled) {
  transform: translateY(0);
}

.quick-command-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.preview-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  padding: 0 24px 24px;
}

.original-outline,
.modified-preview {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.original-outline h4,
.modified-preview h4 {
  margin: 0 0 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main, #374151);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.page-item {
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-sub, #6b7280);
  border: 1px solid var(--border-color, #e5e7eb);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px;
  color: var(--primary, #FF2442);
  font-weight: 600;
  background: linear-gradient(135deg, rgba(255, 240, 242, 0.5) 0%, rgba(255, 255, 255, 0.5) 100%);
  border-radius: 12px;
  border: 1px dashed rgba(255, 36, 66, 0.3);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid var(--primary, #FF2442);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.preview-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
}

.preview-cards::-webkit-scrollbar {
  width: 4px;
}
.preview-cards::-webkit-scrollbar-thumb {
  background: rgba(0,0,0,0.1);
  border-radius: 4px;
}

.preview-card {
  padding: 16px;
  background: white;
  border-radius: 12px;
  border: 1px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.preview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
  border-color: rgba(255, 36, 66, 0.1);
}

.card-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--primary, #FF2442);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-content {
  font-size: 13px;
  color: var(--text-sub, #6b7280);
  line-height: 1.6;
  white-space: pre-wrap;
}

.dialog-actions {
  padding: 24px;
  border-top: 1px solid var(--border-color, #e5e7eb);
  background: rgba(255, 255, 255, 0.3);
}

.modify-summary {
  padding: 16px 20px;
  background: linear-gradient(135deg, #FFF0F2 0%, #FFD4D9 100%);
  border-radius: 12px;
  font-size: 15px;
  color: #D91C36;
  margin-bottom: 24px;
  text-align: center;
  font-weight: 600;
  border: 1px solid rgba(217, 28, 54, 0.2);
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.1);
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-secondary,
.btn-primary {
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
}

.btn-secondary {
  background: white;
  color: var(--text-sub, #4B5563);
  border: 1px solid var(--border-color, #d1d5db);
}

.btn-secondary:hover {
  background: #F9FAFB;
  border-color: #9CA3AF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.btn-primary {
  background: linear-gradient(135deg, #FF2442 0%, #FF6B8A 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.2);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 36, 66, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.dialog-footer {
  padding: 24px;
  border-top: 1px solid var(--border-color, #e5e7eb);
  text-align: center;
}

.dialog-footer .btn-primary {
  width: 100%;
  padding: 14px;
  font-size: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .modify-dialog {
    width: 95%;
    max-height: 95vh;
  }

  .preview-container {
    grid-template-columns: 1fr;
  }

  .quick-commands {
    flex-direction: column;
  }

  .quick-command-btn {
    width: 100%;
    text-align: left;
  }
}
</style>
