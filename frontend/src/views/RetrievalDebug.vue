<script setup>
import { ref, onMounted } from 'vue'
import { getRetrievalDebug } from '../services/api'
import RetrievalStep from '../components/RetrievalStep.vue'

const props = defineProps({
  messageId: { type: [String, Number], required: true },
})
const debug = ref(null)
const loading = ref(true)
const error = ref(null)
const expandedSteps = ref({ plan: true, retrieved: false, reranked: false, reflection: true })

onMounted(async () => {
  try {
    const { data } = await getRetrievalDebug(props.messageId)
    if (data.error) {
      error.value = data.error
    } else {
      debug.value = data
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

function toggleStep(key) {
  expandedSteps.value[key] = !expandedSteps.value[key]
}

function parseDocs(raw) {
  if (!raw) return []
  if (typeof raw === 'string') {
    try { return JSON.parse(raw) } catch { return [] }
  }
  return raw
}

function formatDuration(ms) {
  if (!ms) return ''
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}
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
        <h1 class="text-2xl font-bold text-gray-900">检索调试</h1>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto" />
      </div>

      <!-- Error -->
      <div v-else-if="error" class="card text-center py-8">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <!-- Debug info -->
      <div v-else-if="debug" class="space-y-4">
        <!-- Query -->
        <div class="card">
          <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">查询</h2>
          <p class="text-gray-900">{{ debug.query }}</p>
        </div>

        <!-- Plan -->
        <RetrievalStep
          title="检索计划"
          :expanded="expandedSteps.plan"
          @toggle="toggleStep('plan')"
        >
          <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ debug.plan || '未生成计划' }}</p>
        </RetrievalStep>

        <!-- Retrieved Documents -->
        <RetrievalStep
          :title="`检索到的文档 (${debug.retrieved_count || parseDocs(debug.retrieved_docs).length})`"
          :expanded="expandedSteps.retrieved"
          @toggle="toggleStep('retrieved')"
        >
          <div class="space-y-2">
            <div
              v-for="(doc, i) in parseDocs(debug.retrieved_docs)"
              :key="i"
              class="bg-gray-50 rounded-lg p-3 border border-gray-200"
            >
              <div class="flex items-center gap-2 mb-1">
                <span class="text-xs font-medium text-primary-600">#{{ i + 1 }}</span>
                <span class="text-xs text-gray-500">
                  得分：{{ doc.score?.toFixed(4) || doc.rrf_score?.toFixed(4) || 'N/A' }}
                </span>
                <span v-if="doc.document_id" class="text-xs text-gray-400">
                  文档 #{{ doc.document_id }}
                </span>
                <span v-if="doc.source" class="text-xs px-1.5 py-0.5 rounded bg-gray-200 text-gray-600">
                  {{ doc.source }}
                </span>
              </div>
              <p class="text-xs text-gray-700 line-clamp-3">{{ doc.content }}</p>
            </div>
            <p v-if="!parseDocs(debug.retrieved_docs).length" class="text-sm text-gray-500">
              未检索到文档
            </p>
          </div>
        </RetrievalStep>

        <!-- Reranked Documents -->
        <RetrievalStep
          :title="`重排后的文档 (${debug.reranked_count || parseDocs(debug.reranked_docs).length})`"
          :expanded="expandedSteps.reranked"
          @toggle="toggleStep('reranked')"
        >
          <div class="space-y-2">
            <div
              v-for="(doc, i) in parseDocs(debug.reranked_docs)"
              :key="i"
              class="bg-gray-50 rounded-lg p-3 border border-gray-200"
            >
              <div class="flex items-center gap-2 mb-1">
                <span class="text-xs font-medium text-green-600">#{{ i + 1 }}</span>
                <span class="text-xs text-gray-500">
                  得分：{{ doc.rerank_score?.toFixed(4) || doc.score?.toFixed(4) || 'N/A' }}
                </span>
                <span v-if="doc.document_id" class="text-xs text-gray-400">
                  文档 #{{ doc.document_id }}
                </span>
              </div>
              <p class="text-xs text-gray-700 line-clamp-3">{{ doc.content }}</p>
            </div>
            <p v-if="!parseDocs(debug.reranked_docs).length" class="text-sm text-gray-500">
              无重排文档
            </p>
          </div>
        </RetrievalStep>

        <!-- Reflection -->
        <RetrievalStep
          title="自省结果"
          :expanded="expandedSteps.reflection"
          @toggle="toggleStep('reflection')"
        >
          <div class="flex items-center gap-2">
            <span
              class="text-xs px-2 py-1 rounded-full font-medium"
              :class="debug.reflection_result?.includes('pass')
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'"
            >
              {{ debug.reflection_result || 'N/A' }}
            </span>
          </div>
        </RetrievalStep>
      </div>
    </div>
  </div>
</template>
