<template>
  <section class="testimonials-section">
    <div class="testimonials-container">
      <!-- Section Header -->
      <div class="section-header">
        <h2 class="section-title">创作者的首选工具</h2>
        <p class="section-subtitle">
          来自小红书创作者的真实反馈，看看他们如何用 RedInk 提升创作效率
        </p>
      </div>

      <!-- Testimonials Grid -->
      <div class="testimonials-grid">
        <div
          v-for="(testimonial, index) in testimonials"
          :key="index"
          class="testimonial-card"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <div class="testimonial-rating">
            <svg
              v-for="i in 5"
              :key="i"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="currentColor"
              stroke="none"
            >
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </div>
          <p class="testimonial-text">"{{ testimonial.text }}"</p>
          <div class="testimonial-author">
            <div class="author-avatar">{{ testimonial.avatar }}</div>
            <div class="author-info">
              <div class="author-name">{{ testimonial.name }}</div>
              <div class="author-title">{{ testimonial.title }}</div>
            </div>
          </div>
          <div class="testimonial-stats">
            <div class="stat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
              效率提升 {{ testimonial.efficiency }}
            </div>
            <div class="stat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><path d="M3 9h18"/><path d="M9 21V9"/>
              </svg>
              月均 {{ testimonial.posts }} 篇
            </div>
          </div>
        </div>
      </div>

      <!-- Use Cases -->
      <div class="use-cases">
        <h3 class="use-cases-title">适用场景</h3>
        <div class="use-cases-grid">
          <div
            v-for="(useCase, index) in useCases"
            :key="index"
            class="use-case-item"
          >
            <div class="use-case-icon">{{ useCase.icon }}</div>
            <h4 class="use-case-title">{{ useCase.title }}</h4>
            <p class="use-case-description">{{ useCase.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Testimonial {
  text: string
  name: string
  title: string
  avatar: string
  efficiency: string
  posts: string
}

interface UseCase {
  icon: string
  title: string
  description: string
}

const testimonials: Testimonial[] = [
  {
    text: '以前写一篇小红书文案要花2小时，现在只需10分钟输入主题，AI 就能生成完整的标题和正文，质量还特别高！',
    name: '小美',
    title: '美妆博主 | 50万粉丝',
    avatar: '美',
    efficiency: '10倍',
    posts: '60+'
  },
  {
    text: '最让我惊喜的是图片生成功能，不用再到处找素材了，AI 生成的配图完全符合小红书风格，点赞率提升了30%。',
    name: '阿明',
    title: '生活方式博主 | 20万粉丝',
    avatar: '阿',
    efficiency: '8倍',
    posts: '45+'
  },
  {
    text: '作为技术博主，经常需要分享干货内容。RedInk 的联网搜索功能让我能快速获取最新资讯，内容专业度大幅提升。',
    name: 'Tech哥',
    title: '科技评测博主 | 15万粉丝',
    avatar: '科',
    efficiency: '6倍',
    posts: '30+'
  }
]

const useCases: UseCase[] = [
  {
    icon: '✨',
    title: '产品推广',
    description: '快速生成吸引眼球的产品介绍文案和展示图'
  },
  {
    icon: '📚',
    title: '知识分享',
    description: '将专业知识转化为通俗易懂的小红书笔记'
  },
  {
    icon: '🎨',
    title: '创意设计',
    description: '激发创作灵感，生成独特的设计理念和配图'
  },
  {
    icon: '🍜',
    title: '美食探店',
    description: '记录美食体验，生成诱人的描述和图片'
  }
]
</script>

<style scoped>
.testimonials-section {
  padding: 100px 20px;
  background: var(--bg-body);
}

.testimonials-container {
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

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-bottom: 80px;
}

.testimonial-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.6s ease-out both;
  display: flex;
  flex-direction: column;
}

.testimonial-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.testimonial-rating {
  display: flex;
  gap: 4px;
  color: #fbbf24;
  margin-bottom: 20px;
}

.testimonial-text {
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-main);
  margin-bottom: 24px;
  flex: 1;
}

.testimonial-author {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.author-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  flex-shrink: 0;
}

.author-info {
  flex: 1;
}

.author-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 4px;
}

.author-title {
  font-size: 13px;
  color: var(--text-sub);
}

.testimonial-stats {
  display: flex;
  gap: 16px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-sub);
  font-weight: 500;
}

.stat svg {
  color: var(--primary);
}

.use-cases {
  background: white;
  border-radius: var(--radius-xl);
  padding: 48px;
  box-shadow: var(--shadow-md);
}

.use-cases-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-main);
  text-align: center;
  margin-bottom: 40px;
}

.use-cases-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
}

.use-case-item {
  text-align: center;
  padding: 24px;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
}

.use-case-item:hover {
  background: var(--bg-body);
  transform: translateY(-4px);
}

.use-case-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.use-case-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 8px;
}

.use-case-description {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-sub);
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

/* Responsive */
@media (max-width: 1024px) {
  .testimonials-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .use-cases-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .testimonials-section {
    padding: 60px 20px;
  }

  .section-title {
    font-size: 32px;
  }

  .testimonials-grid {
    grid-template-columns: 1fr;
  }

  .use-cases {
    padding: 32px;
  }

  .use-cases-title {
    font-size: 24px;
  }

  .use-cases-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .use-case-item {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .testimonial-card {
    padding: 24px;
  }
}
</style>
