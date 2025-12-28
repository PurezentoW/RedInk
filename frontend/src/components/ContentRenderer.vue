<template>
  <div class="content-renderer" :class="{ 'is-streaming': isStreaming }">
    <!-- 场景1：正在流式显示 -->
    <div v-if="isStreaming" class="streaming-content">
      <pre class="typewriter-text">
        <!-- 封面类型：显示主标题和副标题 -->
        <template v-if="pageType === 'cover' && (mainTitle || subTitle)">
          <span v-if="mainTitle" class="content-title main-title">{{ mainTitle }}</span>
          <span v-if="mainTitle" class="newline"></span>
          <span v-if="subTitle" class="content-title sub-title">{{ subTitle }}</span>
          <span v-if="subTitle" class="newline"></span>
        </template>
        <!-- 其他类型：显示单行标题 -->
        <template v-else-if="title">
          <span class="content-title">{{ title }}</span>
          <span class="newline"></span>
        </template>
        <span class="content-body">{{ displayBody }}</span>
        <span class="cursor">|</span>
      </pre>
    </div>

    <!-- 场景2：编辑模式 -->
    <textarea
      v-else-if="isEditing"
      ref="textareaRef"
      :value="rawContent"
      class="textarea-paper"
      placeholder="在此输入文案..."
      @input="handleInput"
      @blur="handleBlur"
    />

    <!-- 场景3：只读显示模式（双击可编辑） -->
    <div v-else class="readonly-content" @dblclick="handleStartEdit">
      <!-- 封面类型：显示主标题和副标题 -->
      <template v-if="pageType === 'cover' && (mainTitle || subTitle)">
        <div v-if="mainTitle" class="content-title main-title">{{ mainTitle }}</div>
        <div v-if="subTitle" class="content-title sub-title">{{ subTitle }}</div>
      </template>
      <!-- 其他类型：显示单行标题 -->
      <div v-else-if="title" class="content-title">{{ title }}</div>
      <div class="content-body">{{ displayBody }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { parseTitle, parseBody, parseCoverTitles, parseImageSuggestion, type ParsedTitle } from '../utils/contentParser'

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

// 监听编辑状态变化，自动聚焦
watch(() => props.isEditing, (newVal) => {
  if (newVal) {
    nextTick(() => {
      textareaRef.value?.focus()
    })
  }
})

// 解析封面页的主标题和副标题
const coverTitles = computed<ParsedTitle>(() => {
  const content = props.isStreaming && props.streamingContent
    ? props.streamingContent
    : props.rawContent
  return parseCoverTitles(content)
})

const mainTitle = computed(() => coverTitles.value.mainTitle)
const subTitle = computed(() => coverTitles.value.subTitle)

// 解析普通标题
const title = computed(() => {
  const content = props.isStreaming && props.streamingContent
    ? props.streamingContent
    : props.rawContent
  return parseTitle(content, props.pageType)
})

const displayBody = computed(() => {
  const content = props.isStreaming && props.streamingContent
    ? props.streamingContent
    : props.rawContent

  // 解析配图建议并获取不含配图建议的正文
  const parsed = parseImageSuggestion(content, props.pageType)
  return parsed.bodyContent
})

// 事件处理
const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:content', target.value)
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
  background: #fafafa;
  border-radius: 6px;
  padding: 12px;
  border: 1px solid #f0f0f0;
}

/* 打字机文本样式 */
.typewriter-text {
  font-family: inherit;
  font-size: 15px;
  line-height: 1.8;
  color: #262626;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  padding: 0;
}

/* 流式显示的标题样式 */
.typewriter-text .content-title {
  display: inline;
  font-weight: 600;
  color: #262626;
  line-height: 1.8;
  margin-right: 0.5em;
}

/* 主标题样式（大） */
.typewriter-text .main-title {
  font-size: 18px;
}

/* 副标题样式（小） */
.typewriter-text .sub-title {
  font-size: 15px;
  font-weight: 500;
}

.typewriter-text .newline {
  display: block;
  content: '';
  margin-bottom: 12px;
}

.typewriter-text .content-body {
  display: inline;
  font-size: 15px;
  color: #262626;
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
  min-height: 400px;
  border: none;
  background: transparent;
  padding: 12px;
  font-size: 15px;
  line-height: 1.8;
  color: #262626;
  resize: none;
  font-family: inherit;
  border-radius: 6px;
  transition: background 0.2s;
}

.textarea-paper:focus {
  outline: none;
  background: #fafafa;
}

.textarea-paper::placeholder {
  color: #bfbfbf;
}

/* 只读内容容器 */
.readonly-content {
  flex: 1;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.readonly-content:hover {
  background: #fafafa;
  border-color: #f0f0f0;
}

.readonly-content:active {
  cursor: text;
}

/* 标题样式（只读模式） */
.content-title {
  font-weight: 600;
  color: #262626;
  line-height: 1.4;
  margin: 0;
  word-wrap: break-word;
}

/* 主标题样式（大） */
.content-title.main-title {
  font-size: 18px;
}

/* 副标题样式（小） */
.content-title.sub-title {
  font-size: 15px;
  font-weight: 500;
}

/* 正文样式（只读模式） */
.content-body {
  font-size: 15px;
  line-height: 1.8;
  color: #262626;
  white-space: pre-wrap;
  word-wrap: break-word;
  flex: 1;
}
</style>
