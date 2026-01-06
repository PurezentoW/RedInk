<template>
  <div class="modify-bar">
    <!-- 输入区域 -->
    <div class="modify-input">
      <textarea
        v-model="instruction"
        placeholder="输入修改指令，如：页数太多了，缩短到3页"
        rows="1"
        :disabled="isModifying"
        @keydown.ctrl.enter="handleStartModify"
        class="instruction-textarea"
      />

      <!-- 发送按钮 -->
      <button
        @click="handleStartModify"
        :disabled="!instruction.trim() || isModifying"
        class="send-btn"
      >
        <template v-if="!isModifying">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
          发送
        </template>
        <template v-else>
          <div class="spinner"></div>
          修改中...
        </template>
      </button>
    </div>

    <!-- 预设标签 -->
    <div class="quick-commands">
      <button
        v-for="cmd in quickCommands"
        :key="cmd.label"
        @click="applyQuickCommand(cmd.text)"
        :disabled="isModifying"
        class="command-tag"
        :title="cmd.text"
      >
        {{ cmd.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  isModifying: boolean
}

interface Emits {
  (e: 'modify', instruction: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 状态
const instruction = ref('')

// 快捷指令配置
const quickCommands = [
  { label: "缩短页数", text: "页数太多了，请精简到3-5页，保留核心内容" },
  { label: "增加细节", text: "内容太简单了，请增加更多细节和实用信息" },
  { label: "更专业", text: "请用更专业的语气重新组织内容" },
  { label: "更口语化", text: "请用更轻松、口语化的方式表达" },
  { label: "添加总结", text: "请在最后添加一个总结页" },
  { label: "调整语气", text: "请把语气调整得更友好亲切一些" }
]

// 方法
const applyQuickCommand = (text: string) => {
  instruction.value = text
}

const handleStartModify = () => {
  console.log('🔄 handleStartModify 被调用', {
    instruction: instruction.value,
    isModifying: props.isModifying
  })

  if (!instruction.value.trim() || props.isModifying) {
    console.log('⚠️ 修改被阻止', {
      hasInstruction: !!instruction.value.trim(),
      isModifying: props.isModifying
    })
    return
  }

  const instructionText = instruction.value
  instruction.value = '' // 清空输入框

  console.log('✅ 发送修改事件:', instructionText)
  // 发送修改事件
  emit('modify', instructionText)
}
</script>

<style scoped>
.modify-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  max-width: calc(100vw - 48px);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  padding: 16px;
  z-index: 1000;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.modify-input {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.instruction-textarea {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  font-family: inherit;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.2s;
  min-height: 44px;
  max-height: 80px;
}

.instruction-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.instruction-textarea:disabled {
  background: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

.instruction-textarea::placeholder {
  color: #9ca3af;
}

.send-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  height: 44px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn svg {
  flex-shrink: 0;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.quick-commands {
  display: flex;
  gap: 6px;
  margin-top: 10px;
  overflow-x: auto;
  padding-bottom: 2px;
}

/* 隐藏滚动条但保持可滚动 */
.quick-commands::-webkit-scrollbar {
  height: 3px;
}

.quick-commands::-webkit-scrollbar-track {
  background: transparent;
}

.quick-commands::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 2px;
}

.command-tag {
  padding: 5px 10px;
  background: rgba(102, 126, 234, 0.08);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 14px;
  font-size: 12px;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
}

.command-tag:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-1px);
}

.command-tag:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 768px) {
  .modify-bar {
    bottom: 16px;
    width: calc(100vw - 32px);
    max-width: none;
    padding: 12px;
  }

  .modify-input {
    flex-direction: column;
    gap: 8px;
  }

  .send-btn {
    width: 100%;
    justify-content: center;
    height: 40px;
  }

  .instruction-textarea {
    min-height: 40px;
  }

  .quick-commands {
    flex-wrap: wrap;
    gap: 4px;
  }

  .command-tag {
    font-size: 11px;
    padding: 4px 8px;
  }
}
</style>
