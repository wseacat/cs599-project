<script setup>
import { ref, nextTick } from 'vue'

const emit = defineEmits(['send'])
const props = defineProps({
  disabled: { type: Boolean, default: false },
})

const input = ref('')
let textareaEl = null

function handleSend() {
  const text = input.value.trim()
  if (!text || props.disabled) return
  emit('send', text)
  input.value = ''
  // Reset textarea height after DOM update
  nextTick(() => {
    if (textareaEl) {
      textareaEl.style.height = 'auto'
    }
  })
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="border-t border-gray-200 bg-white p-4">
    <div class="flex items-end gap-3 max-w-4xl mx-auto">
      <textarea
        v-model="input"
        class="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent max-h-40"
        rows="1"
        placeholder="输入关于文档的问题..."
        :disabled="disabled"
        @keydown="handleKeydown"
        @input="$event.target.style.height = 'auto'; $event.target.style.height = $event.target.scrollHeight + 'px'; textareaEl = $event.target"
      />
      <button
        class="btn-primary px-4 py-3 rounded-xl flex-shrink-0"
        :disabled="disabled || !input.trim()"
        @click="handleSend"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
      </button>
    </div>
  </div>
</template>
