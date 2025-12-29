<template>
  <div class="container home-container">
    <!-- 图片网格轮播背景 -->
    <ShowcaseBackground />

    <!-- Hero Area -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="brand-pill">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
          AI 驱动的红墨创作助手
        </div>
        <div class="platform-slogan">
          让传播不再需要门槛，让创作从未如此简单
        </div>
        <h1 class="page-title">灵感一触即发</h1>
        <p class="page-subtitle">输入你的创意主题，让 AI 帮你生成爆款标题、正文和封面图</p>
      </div>

      <!-- 主题输入组合框 -->
      <ComposerInput
        ref="composerRef"
        v-model="topic"
        :loading="loading"
        :useSearch="useSearch"
        @generate="handleGenerate"
        @imagesChange="handleImagesChange"
        @toggleSearch="handleToggleSearch"
      />
    </div>

    <!-- 版权信息 -->
    <div class="page-footer">
      <div class="footer-copyright">
        © 2025 <a href="https://github.com/HisMax/RedInk" target="_blank" rel="noopener noreferrer">RedInk</a> by 默子 (Histone)
      </div>
      <div class="footer-license">
        Licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank" rel="noopener noreferrer">CC BY-NC-SA 4.0</a>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-toast">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'
import { generateOutlineStream, createHistory } from '../api'

// 引入组件
import ShowcaseBackground from '../components/home/ShowcaseBackground.vue'
import ComposerInput from '../components/home/ComposerInput.vue'

const router = useRouter()
const store = useGeneratorStore()

// 状态
const topic = ref('')
const loading = ref(false)
const error = ref('')
const composerRef = ref<InstanceType<typeof ComposerInput> | null>(null)

// 联网搜索开关状态（默认关闭）
const useSearch = ref(false)

// 上传的图片文件
const uploadedImageFiles = ref<File[]>([])

/**
 * 处理图片变化
 */
function handleImagesChange(images: File[]) {
  uploadedImageFiles.value = images
}

/**
 * 切换联网搜索
 */
function handleToggleSearch(enabled: boolean) {
  useSearch.value = enabled
}

/**
 * 生成大纲（使用流式API）
 */
async function handleGenerate() {
  if (!topic.value.trim()) return

  loading.value = true
  error.value = ''

  const imageFiles = uploadedImageFiles.value

  // 初始化流式状态
  store.startStreaming(topic.value.trim())

  // 跳转到OutlineView（打字机效果在那里显示）
  router.push('/outline')

  // 清理 ComposerInput 的预览
  composerRef.value?.clearPreviews()
  uploadedImageFiles.value = []

  try {
    await generateOutlineStream(
      topic.value.trim(),
      imageFiles.length > 0 ? imageFiles : undefined,
      useSearch.value,  // 联网搜索开关
      // onText - 打字机效果核心回调
      (chunk, accumulated) => {
        store.updateStreamingText(chunk, accumulated)
      },
      // onSearchResults - 搜索结果回调
      (results, count) => {
        store.setSearchResults(results)
        console.log(`🔍 收到 ${count} 条搜索结果`)
      },
      // onComplete - 生成完成回调
      async (result) => {
        store.finishStreaming(result)

        // 保存用户上传的图片到 store
        if (imageFiles.length > 0) {
          store.userImages = imageFiles
        } else {
          store.userImages = []
        }

        // 自动创建草稿历史记录
        try {
          const historyResult = await createHistory(
            topic.value.trim(),
            {
              raw: result.outline || '',
              pages: result.pages || []
            }
          )

          if (historyResult.success && historyResult.record_id) {
            store.recordId = historyResult.record_id
            console.log('草稿已自动保存:', historyResult.record_id)
          }
        } catch (err) {
          console.error('自动保存草稿失败:', err)
          // 不阻断用户流程，静默失败
        }
      },
      // onError - 后端返回错误
      (errorMsg) => {
        error.value = errorMsg
        store.isStreaming = false
        store.streamingText = ''
      },
      // onStreamError - 网络或流错误
      (err) => {
        error.value = err.message || '网络错误，请重试'
        store.isStreaming = false
        store.streamingText = ''
      }
    )
  } catch (err: any) {
    error.value = err.message || '网络错误，请重试'
    store.isStreaming = false
    store.streamingText = ''
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home-container {
  max-width: 1100px;
  padding-top: 10px;
  position: relative;
  z-index: 1;
}

/* Hero Section */
.hero-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 50px 60px;
  animation: fadeIn 0.6s ease-out;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(10px);
}

.hero-content {
  margin-bottom: 36px;
}

.brand-pill {
  display: inline-block;
  padding: 6px 16px;
  background: rgba(255, 36, 66, 0.08);
  color: var(--primary);
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 20px;
  letter-spacing: 0.5px;
}

.platform-slogan {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 24px;
  line-height: 1.6;
  letter-spacing: 0.5px;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-sub);
  margin-top: 12px;
}

/* Page Footer */
.page-footer {
  text-align: center;
  padding: 24px 0 16px;
  margin-top: 20px;
}

.footer-copyright {
  font-size: 15px;
  color: #333;
  font-weight: 500;
  margin-bottom: 6px;
}

.footer-copyright a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}

.footer-copyright a:hover {
  text-decoration: underline;
}

.footer-license {
  font-size: 13px;
  color: #999;
}

.footer-license a {
  color: #666;
  text-decoration: none;
}

.footer-license a:hover {
  color: var(--primary);
}

/* Error Toast */
.error-toast {
  position: fixed;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  background: #FF4D4F;
  color: white;
  padding: 12px 24px;
  border-radius: 50px;
  box-shadow: 0 8px 24px rgba(255, 77, 79, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 1000;
  animation: slideUp 0.3s ease-out;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
