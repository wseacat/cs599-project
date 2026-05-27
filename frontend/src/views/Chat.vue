<script setup>
import { watch, nextTick, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '../stores/chat'
import { useConversationsStore } from '../stores/conversations'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'
import CitationPanel from '../components/CitationPanel.vue'

const props = defineProps({
  conversationId: { type: [String, Number], default: null },
})

const route = useRoute()
const chatStore = useChatStore()
const convStore = useConversationsStore()
const messagesContainer = ref(null)
const showCitations = ref(false)
const latestCitations = ref([])

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

watch(() => chatStore.messages.length, scrollToBottom)
watch(() => chatStore.streamingText, scrollToBottom)

async function handleSend(text) {
  const convId = props.conversationId ? Number(props.conversationId) : null
  showCitations.value = false

  try {
    const result = await chatStore.sendMessage(text, convId, true)
    if (result.citations?.length) {
      latestCitations.value = result.citations
      showCitations.value = true
    }
  } catch {
    // error handled in store
  }
}

onMounted(async () => {
  if (props.conversationId) {
    const data = await convStore.fetchConversation(props.conversationId)
    chatStore.loadMessages(data.messages)
  }
})
</script>

<template>
  <div class="flex h-full">
    <!-- Main chat area -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Header -->
      <div class="border-b border-gray-200 bg-white px-6 py-3 flex items-center justify-between">
        <h2 class="text-sm font-medium text-gray-700">
          {{ convStore.currentConversation?.title || '新对话' }}
        </h2>
        <div class="flex items-center gap-2">
          <span v-if="chatStore.isStreaming" class="text-xs text-primary-600 flex items-center gap-1">
            <span class="w-2 h-2 bg-primary-600 rounded-full animate-pulse" />
            思考中...
          </span>
          <button
            v-if="chatStore.isStreaming"
            class="text-xs text-red-600 hover:text-red-800"
            @click="chatStore.cancelStream()"
          >
            取消
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div
        ref="messagesContainer"
        class="flex-1 overflow-y-auto px-6 py-4 space-y-4"
      >
        <!-- Empty state -->
        <div v-if="!chatStore.messages.length && !chatStore.isStreaming" class="flex items-center justify-center h-full">
          <div class="text-center">
            <div class="w-20 h-20 bg-primary-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg class="w-10 h-10 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-700">向您的文档提问</h3>
            <p class="text-sm text-gray-500 mt-1 max-w-md">
              请先上传文档，然后提出问题。AI 将检索相关段落并生成带引用的回答。
            </p>
          </div>
        </div>

        <!-- Message list -->
        <ChatMessage
          v-for="(msg, i) in chatStore.messages"
          :key="i"
          :message="msg"
        />

        <!-- Streaming message -->
        <div v-if="chatStore.isStreaming && chatStore.streamingText" class="flex gap-3 justify-start">
          <div class="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <div class="bg-white border border-gray-200 shadow-sm rounded-2xl rounded-bl-md px-4 py-3 max-w-[75%]">
            <p class="text-sm whitespace-pre-wrap">{{ chatStore.streamingText }}</p>
          </div>
        </div>

        <!-- Loading indicator -->
        <div v-if="chatStore.isStreaming && !chatStore.streamingText" class="flex gap-3 justify-start">
          <div class="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-white animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
          <div class="bg-white border border-gray-200 shadow-sm rounded-2xl rounded-bl-md px-4 py-3">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms" />
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms" />
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms" />
            </div>
          </div>
        </div>

        <!-- Error -->
        <div v-if="chatStore.error" class="flex justify-center">
          <div class="bg-red-50 text-red-700 text-sm px-4 py-2 rounded-lg border border-red-200">
            错误：{{ chatStore.error }}
          </div>
        </div>
      </div>

      <!-- Input -->
      <ChatInput :disabled="chatStore.isStreaming" @send="handleSend" />
    </div>

    <!-- Citation sidebar -->
    <div
      v-if="showCitations && latestCitations.length"
      class="w-80 border-l border-gray-200 bg-gray-50 p-4 overflow-y-auto"
    >
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-semibold text-gray-700">引用来源</h3>
        <button class="text-gray-400 hover:text-gray-600" @click="showCitations = false">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <CitationPanel :citations="latestCitations" />
    </div>
  </div>
</template>
