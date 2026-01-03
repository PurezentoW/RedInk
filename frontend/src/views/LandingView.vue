<template>
  <div class="landing-container">
    <!-- Hero Section -->
    <HeroSection @start-creating="handleStartCreating" />

    <!-- Features Section -->
    <FeaturesSection />

    <!-- Testimonials Section -->
    <TestimonialsSection />

    <!-- Footer -->
    <footer class="landing-footer">
      <div class="footer-content">
        <div class="footer-links">
          <a href="https://github.com/HisMax/RedInk" target="_blank" rel="noopener noreferrer">GitHub</a>
          <span class="separator">•</span>
          <a href="https://github.com/HisMax/RedInk/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">许可证</a>
          <span class="separator">•</span>
          <router-link to="/settings">设置</router-link>
        </div>
        <div class="footer-copyright">
          © 2025 RedInk by 默子 (Histone) • CC BY-NC-SA 4.0
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import HeroSection from '../components/landing/HeroSection.vue'
import FeaturesSection from '../components/landing/FeaturesSection.vue'
import TestimonialsSection from '../components/landing/TestimonialsSection.vue'

const router = useRouter()

/**
 * 处理"开始创作"按钮点击
 */
function handleStartCreating() {
  router.push('/')
}
</script>

<style scoped>
.landing-container {
  min-height: 100vh;
  background: var(--bg-body);
}

.landing-footer {
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  padding: 40px 20px;
  margin-top: 80px;
}

.footer-content {
  max-width: 1100px;
  margin: 0 auto;
  text-align: center;
}

.footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 14px;
}

.footer-links a,
.footer-links router-link {
  color: var(--text-sub);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-links a:hover,
.footer-links router-link:hover {
  color: var(--primary);
}

.separator {
  color: var(--border-color);
}

.footer-copyright {
  font-size: 13px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .footer-links {
    flex-wrap: wrap;
  }

  .separator {
    display: none;
  }
}
</style>
