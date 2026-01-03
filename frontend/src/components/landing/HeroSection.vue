<template>
  <section class="hero-section">
    <div class="hero-container">
      <!-- Badge -->
      <div class="hero-badge">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
        </svg>
        AI 驱动的红墨创作助手
      </div>

      <!-- Title -->
      <h1 class="hero-title">
        让传播不再需要门槛<br/>
        让创作从未如此简单
      </h1>

      <!-- Subtitle -->
      <p class="hero-subtitle">
        输入一句话，AI 自动生成爆款标题、正文和封面图<br/>
        专为小红书创作者设计，让内容创作效率提升 10 倍
      </p>

      <!-- CTA Buttons -->
      <div class="hero-actions">
        <button class="btn btn-primary" @click="$emit('startCreating')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          立即开始创作
        </button>
        <a href="https://github.com/HisMax/RedInk" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          查看 GitHub
        </a>
      </div>

      <!-- Stats -->
      <div class="hero-stats">
        <div class="stat-item">
          <div class="stat-value">10x</div>
          <div class="stat-label">创作效率提升</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">AI</div>
          <div class="stat-label">智能生成</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">100%</div>
          <div class="stat-label">开源免费</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
/**
 * HeroSection - 着陆页首屏区域
 *
 * 事件：
 * @startCreating - 点击"立即开始创作"按钮时触发
 */
defineEmits<{
  startCreating: []
}>()
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #fff5f6 0%, #fff 100%);
  padding: 120px 20px 80px;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(255, 36, 66, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.hero-section::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -5%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(255, 36, 66, 0.05) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.hero-container {
  max-width: 1100px;
  margin: 0 auto;
  text-align: center;
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: rgba(255, 36, 66, 0.08);
  color: var(--primary);
  border-radius: 100px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 32px;
  letter-spacing: 0.5px;
  animation: fadeInUp 0.6s ease-out;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  line-height: 1.2;
  color: var(--text-main);
  margin-bottom: 24px;
  letter-spacing: -0.5px;
  animation: fadeInUp 0.6s ease-out 0.1s both;
}

.hero-subtitle {
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-sub);
  max-width: 700px;
  margin: 0 auto 48px;
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 64px;
  animation: fadeInUp 0.6s ease-out 0.3s both;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 100px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  text-decoration: none;
}

.btn-primary {
  background: var(--primary);
  color: white;
  box-shadow: 0 4px 16px rgba(255, 36, 66, 0.24);
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 36, 66, 0.32);
}

.btn-primary:active {
  transform: translateY(0);
  background: var(--primary-active);
}

.btn-secondary {
  background: white;
  color: var(--text-main);
  border: 2px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}

.btn-secondary:hover {
  border-color: var(--border-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.hero-stats {
  display: flex;
  gap: 64px;
  justify-content: center;
  animation: fadeInUp 0.6s ease-out 0.4s both;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-sub);
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .hero-section {
    padding: 80px 20px 60px;
  }

  .hero-title {
    font-size: 36px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .btn {
    width: 100%;
    max-width: 280px;
    justify-content: center;
  }

  .hero-stats {
    flex-direction: column;
    gap: 32px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 28px;
  }

  .hero-subtitle {
    font-size: 14px;
  }

  .stat-value {
    font-size: 28px;
  }
}
</style>
