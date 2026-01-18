<template>
  <!-- 大纲查看模态框 -->
  <div v-if="visible && pages" class="outline-modal-overlay" @click="$emit('close')">
    <div class="outline-modal-content" @click.stop>
      <div class="outline-modal-header">
        <h3>完整大纲</h3>
        <button class="close-icon" @click="$emit('close')">×</button>
      </div>
      <div class="outline-modal-body">
        <div v-for="(page, idx) in pages" :key="idx" class="outline-page-card">
          <div class="outline-page-card-header">
            <span class="page-badge">P{{ idx + 1 }}</span>
            <span class="page-type-badge" :class="page.type">{{ getPageTypeName(page.type) }}</span>
            <span class="word-count">{{ page.content.length }} 字</span>
          </div>
          <div class="outline-page-card-content">{{ page.content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 大纲查看模态框组件
 *
 * 以卡片形式展示大纲的每一页内容，包含：
 * - 页码标识
 * - 页面类型（封面/内容/总结）
 * - 字数统计
 * - 完整内容
 */

// 定义页面类型
interface Page {
  type: 'cover' | 'content' | 'summary'
  content: string
}

// 定义 Props
defineProps<{
  visible: boolean
  pages: Page[] | null
}>()

// 定义 Emits
defineEmits<{
  (e: 'close'): void
}>()

/**
 * 获取页面类型的中文名称
 */
function getPageTypeName(type: string): string {
  const names: Record<string, string> = {
    cover: '封面',
    content: '内容',
    summary: '总结'
  }
  return names[type] || '内容'
}
</script>

<style scoped>
/* 模态框遮罩层 - 玻璃态效果 */
.outline-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 模态框内容容器 - 玻璃态设计 */
.outline-modal-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  width: 100%;
  max-width: 800px;
  max-height: 85vh;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 模态框头部 */
.outline-modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
}

.outline-modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1F2937;
  letter-spacing: -0.3px;
}

/* 关闭按钮 */
.close-icon {
  width: 36px;
  height: 36px;
  background: rgba(0, 0, 0, 0.03);
  border: none;
  border-radius: 8px;
  font-size: 20px;
  cursor: pointer;
  color: #6B7280;
  padding: 0;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.close-icon:hover {
  background: rgba(255, 36, 66, 0.1);
  color: #FF2442;
  transform: rotate(90deg);
}

/* 模态框主体（可滚动） */
.outline-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  background: linear-gradient(135deg, #FAFAFA 0%, #F4F5F7 100%);
}

/* 美化滚动条 */
.outline-modal-body::-webkit-scrollbar {
  width: 6px;
}

.outline-modal-body::-webkit-scrollbar-track {
  background: transparent;
}

.outline-modal-body::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.outline-modal-body::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 大纲页面卡片 */
.outline-page-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.outline-page-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: rgba(255, 36, 66, 0.2);
}

.outline-page-card:last-child {
  margin-bottom: 0;
}

/* 卡片头部 */
.outline-page-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

/* 页码标识 */
.page-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 24px;
  padding: 0 10px;
  background: linear-gradient(135deg, #FF2442 0%, #FF6B8A 100%);
  color: white;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  font-family: 'Inter', sans-serif;
  box-shadow: 0 2px 8px rgba(255, 36, 66, 0.2);
}

/* 页面类型标识 */
.page-type-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.page-type-badge.cover {
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  color: #1976D2;
  border: 1px solid rgba(25, 118, 210, 0.2);
}

.page-type-badge.content {
  background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%);
  color: #7B1FA2;
  border: 1px solid rgba(123, 31, 162, 0.2);
}

.page-type-badge.summary {
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
  color: #388E3C;
  border: 1px solid rgba(56, 142, 60, 0.2);
}

/* 字数统计 */
.word-count {
  margin-left: auto;
  font-size: 12px;
  color: #9CA3AF;
  font-weight: 500;
}

/* 卡片内容 */
.outline-page-card-content {
  font-size: 15px;
  line-height: 1.8;
  color: #1F2937;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .outline-modal-overlay {
    padding: 20px;
  }

  .outline-modal-content {
    max-height: 90vh;
    border-radius: 20px;
  }

  .outline-modal-header {
    padding: 20px 24px;
  }

  .outline-modal-header h3 {
    font-size: 18px;
  }

  .outline-modal-body {
    padding: 20px 24px;
  }

  .outline-page-card {
    padding: 20px;
    border-radius: 12px;
  }

  .outline-page-card-header {
    margin-bottom: 14px;
    padding-bottom: 14px;
  }

  .outline-page-card-content {
    font-size: 14px;
  }
}
</style>
