<template>
  <div class="content-renderer" :class="{ 'is-streaming': isStreaming }">
    <!-- 场景1：正在流式显示 -->
    <div v-if="isStreaming" class="streaming-content">
      <div class="streaming-text">
        <!-- 所有页面类型：直接显示完整的 Markdown 渲染结果（包含标题） -->
        <div class="content-body markdown-body streaming-body full-content" v-html="displayBody"></div>
        <span class="cursor">|</span>
      </div>
    </div>

    <!-- 场景2：编辑模式 -->
    <textarea
      v-else-if="isEditing"
      ref="textareaRef"
      :value="displayBody"
      class="textarea-paper"
      placeholder="在此输入文案..."
      @input="handleInput"
      @blur="handleBlur"
    />

    <!-- 场景3：只读显示模式（双击可编辑） -->
    <div v-else class="readonly-content" @dblclick="handleStartEdit">
      <!-- 所有页面类型：直接显示完整的 Markdown 渲染结果（包含标题） -->
      <div class="content-body markdown-body full-content" v-html="displayBody"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { parseImageSuggestion } from '../utils/contentParser'
import MarkdownIt from 'markdown-it'

interface Props {
  rawContent: string
  isStreaming: boolean
  isEditing: boolean
  streamingContent?: string
  pageType?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:content': [value: string]
  'blur': []
  'start-edit': []
}>()

// Textarea 引用
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// 初始化 Markdown-it
const md = new MarkdownIt({
  html: false,        // 禁用 HTML 标签
  linkify: true,      // 自动转换 URL 为链接
  typographer: true,  // 启用一些语言中立的替换和引号美化
  breaks: true,       // 转换 \n 为 <br>
})

// 监听编辑状态变化，自动聚焦
watch(() => props.isEditing, (newVal) => {
  if (newVal) {
    nextTick(() => {
      textareaRef.value?.focus()
    })
  }
})

// 分离正文和配图建议
const parsedContent = computed(() => {
  const content = props.isStreaming && props.streamingContent
    ? props.streamingContent
    : props.rawContent

  // 清理页面类型标记和标签
  const cleaned = content
    .replace(/^\[封面\]\s*/i, '')      // 移除 [封面] 标记
    .replace(/^\[内容\]\s*/i, '')      // 移除 [内容] 标记
    .replace(/^\[总结\]\s*/i, '')      // 移除 [总结] 标记
    .replace(/<\/?page>/gi, '')       // 移除 <page> 标签
    .trim()

  return parseImageSuggestion(cleaned, props.pageType)
})

// 显示内容（根据模式决定）
const displayBody = computed(() => {
  const { bodyContent } = parsedContent.value

  // 编辑模式和只读模式都只显示正文
  if (props.isEditing) {
    // 编辑模式：返回原始正文（用于 textarea）
    return bodyContent
  } else {
    // 只读模式：渲染 Markdown
    return md.render(bodyContent)
  }
})

// 事件处理
const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  const newBodyContent = target.value

  // 重新组合正文和原有的配图建议
  const { imageSuggestion } = parsedContent.value
  let fullContent = newBodyContent

  if (imageSuggestion) {
    const label = '配图建议'
    const separator = fullContent && !fullContent.endsWith('\n') ? '\n' : ''
    fullContent = `${fullContent}${separator}${label}：${imageSuggestion}`
  }

  emit('update:content', fullContent)
}

const handleBlur = () => {
  emit('blur')
}

const handleStartEdit = () => {
  emit('start-edit')
}
</script>

<style scoped>
/* 流式内容容器 */
.streaming-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 6px;
  padding: 12px 16px;
  border: 1px solid rgba(24, 144, 255, 0.2);
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  box-sizing: border-box;
  box-shadow: 0 0 0 1px rgba(24, 144, 255, 0.1);
}

/* 流式文本容器 */
.streaming-text {
  font-family: inherit;
  font-size: 15px;
  line-height: 1.8;
  color: #262626;
  position: relative;
  overflow-wrap: break-word;
  word-break: break-word;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 流式内容的正文样式 */
.streaming-text .streaming-body {
  display: block;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 流式内容的完整样式（包含标题） */
.streaming-text .full-content {
  display: block;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 光标样式 */
.cursor {
  display: inline-block;
  animation: blink 1s step-end infinite;
  color: #1890ff;
  font-weight: 600;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 编辑模式 textarea */
.textarea-paper {
  flex: 1;
  width: 100%;
  min-height: 300px;
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(250, 250, 250, 0.8);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  padding: 12px;
  font-size: 15px;
  line-height: 1.8;
  color: #262626;
  resize: vertical;
  font-family: inherit;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.textarea-paper:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(255, 36, 66, 0.3);
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.1);
}

.textarea-paper::placeholder {
  color: #bfbfbf;
}

/* 只读内容容器 */
.readonly-content {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.readonly-content:hover {
  background: rgba(249, 250, 251, 0.8);
  border-color: rgba(0, 0, 0, 0.05);
}

.readonly-content:active {
  cursor: text;
}

/* 正文样式 */
.content-body {
  font-size: 15px;
  line-height: 1.8;
  color: #262626;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 完整内容样式（包含标题的 Markdown） */
.full-content {
  white-space: normal;
  overflow-wrap: break-word;
  word-break: break-word;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* Markdown 样式 */
.markdown-body {
  white-space: normal;
  overflow-wrap: break-word;
  word-break: break-word;
  width: 100%;
  max-width: 100%;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  font-weight: 600;
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #262626;
  max-width: 100%;
  overflow-wrap: break-word;
  word-break: break-word;
}

.markdown-body h1 { font-size: 1.5em; }
.markdown-body h2 { font-size: 1.3em; }
.markdown-body h3 { font-size: 1.15em; }
.markdown-body h4 { font-size: 1.05em; }

.markdown-body p {
  margin: 0.5em 0;
  max-width: 100%;
  overflow-wrap: break-word;
  word-break: break-word;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 0.5em;
  padding-right: 0.5em;
  margin: 0.5em 0;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 100%;
  list-style-position: inside;
  width: 100%;
  box-sizing: border-box;
}

.markdown-body li {
  margin: 0.25em 0;
  padding-left: 0.3em;
  padding-right: 0;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 100%;
  box-sizing: border-box;
  display: list-item;
}

.markdown-body li::marker {
  display: inline-block;
  margin-right: 0.5em;
}

/* 确保列表内容正确显示 */
.markdown-body li > * {
  overflow-wrap: break-word;
  word-break: break-word;
}

.markdown-body code {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
  font-family: 'Courier New', monospace;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-all;
  max-width: 100%;
}

.markdown-body pre {
  background: rgba(0, 0, 0, 0.05);
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.5em 0;
  max-width: 100%;
}

.markdown-body pre code {
  background: none;
  padding: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-all;
}

.markdown-body strong {
  font-weight: 600;
}

.markdown-body em {
  font-style: italic;
}

.markdown-body a {
  color: #1890ff;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body blockquote {
  border-left: 4px solid #d9d9d9;
  padding-left: 1em;
  margin: 0.5em 0;
  color: #595959;
}

/* 美化滚动条 */
.streaming-content::-webkit-scrollbar,
.textarea-paper::-webkit-scrollbar,
.readonly-content::-webkit-scrollbar {
  width: 6px;
}

.streaming-content::-webkit-scrollbar-track,
.textarea-paper::-webkit-scrollbar-track,
.readonly-content::-webkit-scrollbar-track {
  background: transparent;
}

.streaming-content::-webkit-scrollbar-thumb,
.textarea-paper::-webkit-scrollbar-thumb,
.readonly-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.streaming-content::-webkit-scrollbar-thumb:hover,
.textarea-paper::-webkit-scrollbar-thumb:hover,
.readonly-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}
</style>
