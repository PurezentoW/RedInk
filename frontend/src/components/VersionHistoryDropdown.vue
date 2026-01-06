<template>
  <div class="version-dropdown" ref="dropdownRef">
    <button @click="toggleDropdown" class="dropdown-toggle" ref="toggleRef">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
      </svg>
      <span>历史版本</span>
      <span v-if="!isLoading" class="version-count">({{ versions.length }})</span>
      <svg class="dropdown-arrow" :class="{ rotated: isOpen }" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </button>

    <Teleport to="body">
      <div v-if="isOpen" class="dropdown-menu" :style="menuStyle">
        <div v-if="isLoading" class="loading">
          <div class="spinner-small"></div>
          加载中...
        </div>

        <div v-else-if="versions.length === 0" class="empty">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#d1d5db" stroke-width="1.5">
            <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
            <path d="M2 17l10 5 10-5"></path>
            <path d="M2 12l10 5 10-5"></path>
          </svg>
          <p>暂无历史版本</p>
          <p class="empty-hint">修改大纲后会自动保存版本</p>
        </div>

        <div v-else class="version-list">
          <div
            v-for="version in versions"
            :key="version.version_id"
            class="version-item"
          >
            <div class="version-header">
              <span class="version-time">{{ formatTime(version.created_at) }}</span>
              <span class="version-tag">{{ version.version_id.split('_')[0] }}</span>
            </div>
            <div class="version-summary">
              {{ version.modification.summary }}
            </div>
            <div class="version-meta">
              {{ version.outline.pages.length }} 页 · {{ truncateInstruction(version.modification.instruction) }}
            </div>
            <div class="version-actions">
              <button @click="handleRestoreVersion(version)" class="btn-restore">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="1 4 1 10 7 10"></polyline>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
                </svg>
                恢复此版本
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Version {
  version_id: string
  created_at: string
  modification: {
    instruction: string
    summary: string
  }
  outline: {
    pages: any[]
  }
}

interface Props {
  recordId: string | null
}

interface Emits {
  (e: 'restore', version: Version): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 状态
const isOpen = ref(false)
const isLoading = ref(false)
const versions = ref<Version[]>([])
const dropdownRef = ref<HTMLElement | null>(null)
const toggleRef = ref<HTMLElement | null>(null)
const menuStyle = ref<Record<string, string>>({})

// 格式化时间
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 小于1分钟
  if (diff < 60 * 1000) {
    return '刚刚'
  }

  // 小于1小时
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000))
    return `${minutes}分钟前`
  }

  // 小于24小时
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    return `${hours}小时前`
  }

  // 大于24小时，显示日期
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')
  return `${month}月${day}日 ${hour}:${minute}`
}

// 截断指令
const truncateInstruction = (instruction: string) => {
  if (instruction.length <= 20) {
    return instruction
  }
  return instruction.substring(0, 20) + '...'
}

// 切换下拉菜单
const toggleDropdown = async () => {
  isOpen.value = !isOpen.value

  if (isOpen.value) {
    // 计算菜单位置
    await updateMenuPosition()
    if (props.recordId) {
      await loadVersions()
    }
  }
}

// 更新菜单位置
const updateMenuPosition = () => {
  if (!toggleRef.value) return

  const rect = toggleRef.value.getBoundingClientRect()
  menuStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 8}px`,
    right: `${window.innerWidth - rect.right}px`,
  }
}

// 加载版本列表
const loadVersions = async () => {
  if (!props.recordId) {
    return
  }

  isLoading.value = true

  try {
    // 调用后端API获取版本列表
    const response = await fetch(`/api/history/${props.recordId}/versions`)
    const data = await response.json()

    if (data.success) {
      versions.value = data.versions || []
    } else {
      console.error('加载版本失败:', data.error)
    }
  } catch (error) {
    console.error('加载版本异常:', error)
  } finally {
    isLoading.value = false
  }
}

// 恢复版本
const handleRestoreVersion = (version: Version) => {
  if (confirm(`确定要恢复到版本 ${version.version_id.split('_')[0]} 吗？\n\n${version.modification.summary}\n\n恢复前会自动保存当前版本。`)) {
    emit('restore', version)
    isOpen.value = false
  }
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('scroll', updateMenuPosition)
  window.addEventListener('resize', updateMenuPosition)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('scroll', updateMenuPosition)
  window.removeEventListener('resize', updateMenuPosition)
})
</script>

<style scoped>
.version-dropdown {
  position: relative;
  display: inline-block;
  z-index: 9999;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
  transition: all 0.2s;
}

.dropdown-toggle:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.dropdown-arrow {
  transition: transform 0.3s;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.version-count {
  padding: 2px 8px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.dropdown-menu {
  width: 360px;
  max-height: 500px;
  overflow-y: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 99999;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  color: #6b7280;
  font-size: 14px;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 24px;
  text-align: center;
}

.empty p {
  margin: 8px 0 0;
  font-size: 14px;
  color: #6b7280;
}

.empty-hint {
  font-size: 12px !important;
  color: #9ca3af !important;
}

.version-list {
  padding: 8px;
}

.version-item {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.version-item:last-child {
  margin-bottom: 0;
}

.version-item:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.version-time {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

.version-tag {
  padding: 2px 8px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.version-summary {
  font-size: 14px;
  color: #1f2937;
  margin-bottom: 8px;
  font-weight: 500;
  line-height: 1.4;
}

.version-meta {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 12px;
}

.version-actions {
  display: flex;
  gap: 8px;
}

.btn-restore {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #6b7280;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-restore:hover {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

/* 响应式 */
@media (max-width: 768px) {
  .dropdown-menu {
    width: 300px;
    max-height: 400px;
  }
}
</style>
