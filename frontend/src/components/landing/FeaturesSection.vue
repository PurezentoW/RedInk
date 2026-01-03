<template>
  <section class="features-section">
    <div class="features-container">
      <!-- Section Header -->
      <div class="section-header">
        <h2 class="section-title">强大功能，简单操作</h2>
        <p class="section-subtitle">
          集成最新 AI 技术，从创意到成品，一站式解决内容创作难题
        </p>
      </div>

      <!-- Features Grid -->
      <div class="features-grid">
        <div
          v-for="(feature, index) in features"
          :key="index"
          class="feature-card"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <div class="feature-icon" :style="{ background: feature.color }">
            <svg v-html="feature.icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
        </div>
      </div>

      <!-- Highlight Feature -->
      <div class="feature-highlight">
        <div class="highlight-content">
          <div class="highlight-badge">核心优势</div>
          <h3 class="highlight-title">流式生成，实时预览</h3>
          <p class="highlight-description">
            采用先进的流式传输技术，AI 生成的内容实时显示在屏幕上
            像打字机一样逐字呈现，让创作过程充满惊喜和期待
          </p>
          <ul class="highlight-features">
            <li>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              实时流式输出，无需等待
            </li>
            <li>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              智能大纲结构化呈现
            </li>
            <li>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              支持联网搜索增强
            </li>
          </ul>
        </div>
        <div class="highlight-visual">
          <div class="visual-card">
            <div class="visual-header">
              <div class="visual-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            <div class="visual-content">
              <div class="typing-animation">
                <span class="typing-text">{{ typingText }}</span>
                <span class="cursor">|</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Feature {
  icon: string
  title: string
  description: string
  color: string
}

const features: Feature[] = [
  {
    icon: '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
    title: '智能大纲生成',
    description: 'AI 自动分析主题，生成结构化大纲，包含爆款标题和章节规划',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    icon: '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>',
    title: 'AI 图片生成',
    description: '根据大纲内容自动生成精美封面图和配图，支持多种风格',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    icon: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    title: '联网搜索增强',
    description: '集成多种搜索引擎，实时获取最新信息，让内容更准确专业',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    icon: '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>',
    title: '内容编辑优化',
    description: '可视化编辑器，支持实时修改、预览，一键导出多种格式',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  },
  {
    icon: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    title: '批量下载管理',
    description: '支持图片批量下载、压缩优化，自动保存历史记录',
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  },
  {
    icon: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    title: '隐私安全保障',
    description: '本地部署，数据完全掌控，开源代码透明可审计',
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)'
  }
]

const typingText = ref('')
const demoText = '正在生成爆款内容...'
let charIndex = 0

onMounted(() => {
  typeWriter()
})

function typeWriter() {
  if (charIndex < demoText.length) {
    typingText.value += demoText.charAt(charIndex)
    charIndex++
    setTimeout(typeWriter, 100)
  } else {
    setTimeout(() => {
      typingText.value = ''
      charIndex = 0
      typeWriter()
    }, 2000)
  }
}
</script>

<style scoped>
.features-section {
  padding: 100px 20px;
  background: white;
}

.features-container {
  max-width: 1100px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 64px;
}

.section-title {
  font-size: 40px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 16px;
  letter-spacing: -0.5px;
}

.section-subtitle {
  font-size: 18px;
  color: var(--text-sub);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-bottom: 80px;
}

.feature-card {
  background: var(--bg-body);
  border-radius: var(--radius-lg);
  padding: 32px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.6s ease-out both;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.feature-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 20px;
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 12px;
}

.feature-description {
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-sub);
}

.feature-highlight {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
  background: linear-gradient(135deg, #fff5f6 0%, #fff 100%);
  border-radius: var(--radius-xl);
  padding: 48px;
  box-shadow: var(--shadow-md);
}

.highlight-content {
  flex: 1;
}

.highlight-badge {
  display: inline-block;
  padding: 6px 16px;
  background: rgba(255, 36, 66, 0.1);
  color: var(--primary);
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 20px;
}

.highlight-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 16px;
  line-height: 1.3;
}

.highlight-description {
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-sub);
  margin-bottom: 32px;
}

.highlight-features {
  list-style: none;
  padding: 0;
  margin: 0;
}

.highlight-features li {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 15px;
  color: var(--text-main);
  font-weight: 500;
}

.highlight-features li svg {
  color: var(--primary);
  flex-shrink: 0;
}

.highlight-visual {
  flex: 1;
}

.visual-card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.visual-header {
  background: #f5f5f5;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.visual-dots {
  display: flex;
  gap: 6px;
}

.visual-dots span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ddd;
}

.visual-dots span:nth-child(1) {
  background: #ff5f57;
}

.visual-dots span:nth-child(2) {
  background: #febc2e;
}

.visual-dots span:nth-child(3) {
  background: #28c840;
}

.visual-content {
  padding: 40px;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.typing-animation {
  font-family: 'Courier New', monospace;
  font-size: 18px;
  color: var(--text-main);
}

.cursor {
  display: inline-block;
  animation: blink 1s infinite;
  color: var(--primary);
  font-weight: bold;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .feature-highlight {
    grid-template-columns: 1fr;
    gap: 40px;
  }
}

@media (max-width: 768px) {
  .features-section {
    padding: 60px 20px;
  }

  .section-title {
    font-size: 32px;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .feature-highlight {
    padding: 32px;
  }

  .highlight-title {
    font-size: 24px;
  }

  .visual-content {
    padding: 24px;
  }
}

@media (max-width: 480px) {
  .feature-card {
    padding: 24px;
  }

  .feature-icon {
    width: 56px;
    height: 56px;
  }
}
</style>
