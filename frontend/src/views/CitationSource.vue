<script setup>
import { ref, onMounted } from 'vue'
import { getMessage } from '../services/api'

const props = defineProps({
  messageId: { type: [String, Number], required: true },
})
const loading = ref(true)
const citations = ref([])
const message = ref(null)
const error = ref(null)

onMounted(async () => {
  try {
    const { data } = await getMessage(props.messageId)
    message.value = data
    if (data.citations_json) {
      citations.value = JSON.parse(data.citations_json)
    }
  } catch (err) {
    error.value = err.message || 'Failed to load message'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="max-w-4xl mx-auto px-6 py-8">
      <div class="flex items-center gap-3 mb-6">
        <router-link
          :to="{ name: 'Chat' }"
          class="text-gray-400 hover:text-gray-600"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </router-link>
        <h1 class="text-2xl font-bold text-gray-900">引用来源</h1>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto" />
      </div>

      <!-- Error -->
      <div v-else-if="error" class="card text-center py-8">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <!-- Original message -->
      <div v-if="message" class="card mb-6">
        <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">原始回答</h2>
        <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ message.content }}</p>
      </div>

      <!-- Citations -->
      <div v-if="citations.length" class="space-y-4">
        <h2 class="text-lg font-semibold text-gray-900">
          {{ citations.length }} 个来源
        </h2>

        <div
          v-for="(cite, i) in citations"
          :key="i"
          class="card"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="w-7 h-7 bg-primary-100 text-primary-700 rounded-lg flex items-center justify-center text-sm font-bold">
                {{ i + 1 }}
              </span>
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ cite.filename || '未知文档' }}
                </p>
                <p class="text-xs text-gray-500">
                  <span v-if="cite.page">第 {{ cite.page }} 页</span>
                  <span v-if="cite.page && cite.document_id"> · </span>
                  <span v-if="cite.document_id">文档 #{{ cite.document_id }}</span>
                  <span v-if="cite.chunk_id"> · 片段 #{{ cite.chunk_id }}</span>
                </p>
              </div>
            </div>
          </div>

          <div v-if="cite.snippet" class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <p class="text-sm text-gray-700 leading-relaxed">
              <span class="text-primary-600 font-serif text-lg leading-none">"</span>
              {{ cite.snippet }}
              <span class="text-primary-600 font-serif text-lg leading-none">"</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!loading && !error" class="text-center py-12 text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
          />
        </svg>
        <p class="text-lg">未找到引用</p>
        <p class="text-sm mt-1">此消息可能没有关联的引用来源</p>
      </div>
    </div>
  </div>
</template>
