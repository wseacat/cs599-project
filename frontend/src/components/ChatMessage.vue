<script setup>
import { useRouter } from 'vue-router'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps({
  message: { type: Object, required: true },
})

const router = useRouter()
const isUser = props.message.role === 'user'

function viewCitations() {
  if (props.message.message_id) {
    router.push({ name: 'CitationSource', params: { messageId: props.message.message_id } })
  }
}

function viewDebug() {
  if (props.message.message_id) {
    router.push({ name: 'RetrievalDebug', params: { messageId: props.message.message_id } })
  }
}
</script>

<template>
  <div class="flex gap-3" :class="isUser ? 'justify-end' : 'justify-start'">
    <!-- Avatar -->
    <div
      v-if="!isUser"
      class="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0"
    >
      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
        />
      </svg>
    </div>

    <!-- Bubble -->
    <div
      class="max-w-[75%] rounded-2xl px-4 py-3"
      :class="isUser
        ? 'bg-primary-600 text-white rounded-br-md'
        : 'bg-white border border-gray-200 shadow-sm rounded-bl-md'"
    >
      <!-- User text -->
      <p v-if="isUser" class="text-sm whitespace-pre-wrap">{{ message.content }}</p>

      <!-- Assistant text -->
      <div v-else>
        <MarkdownRenderer :content="message.content" />

        <!-- Action buttons -->
        <div
          v-if="message.citations?.length || message.message_id"
          class="flex gap-2 mt-3 pt-2 border-t border-gray-100"
        >
          <button
            v-if="message.citations?.length"
            class="text-xs text-primary-600 hover:text-primary-800 flex items-center gap-1"
            @click="viewCitations"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
              />
            </svg>
            {{ message.citations.length }} 个来源
          </button>
          <button
            v-if="message.message_id"
            class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
            @click="viewDebug"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            调试
          </button>
        </div>
      </div>
    </div>

    <!-- User avatar -->
    <div
      v-if="isUser"
      class="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0"
    >
      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
        />
      </svg>
    </div>
  </div>
</template>
