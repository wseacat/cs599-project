<script setup>
import { useDocumentsStore } from '../stores/documents'

const props = defineProps({
  doc: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})

const emit = defineEmits(['process', 'delete', 'viewChunks', 'toggle-select'])
const store = useDocumentsStore()

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

const statusLabels = {
  pending: '待处理',
  completed: '已完成',
  failed: '处理失败',
}

const fileIcons = {
  pdf: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z',
  docx: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  txt: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
}
</script>

<template>
  <div class="card flex items-start gap-4" :class="{ 'ring-2 ring-primary-500 bg-primary-50/30': selected }">
    <!-- Checkbox -->
    <label class="flex items-center pt-1 cursor-pointer flex-shrink-0">
      <input
        type="checkbox"
        :checked="selected"
        class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
        @change="$emit('toggle-select', doc.id)"
      />
    </label>

    <!-- Icon -->
    <div class="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center flex-shrink-0">
      <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          :d="fileIcons[doc.file_type] || fileIcons.txt"
        />
      </svg>
    </div>

    <!-- Info -->
    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-gray-900 truncate">{{ doc.filename }}</p>
      <div class="flex items-center gap-2 mt-1">
        <span
          class="text-xs px-2 py-0.5 rounded-full"
          :class="statusColors[doc.status] || 'bg-gray-100 text-gray-600'"
        >
          {{ statusLabels[doc.status] || doc.status }}
        </span>
        <span class="text-xs text-gray-500">{{ doc.chunk_count }} 个片段</span>
        <span class="text-xs text-gray-400">
          {{ new Date(doc.created_at).toLocaleDateString('zh-CN') }}
        </span>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-2 flex-shrink-0">
      <button
        v-if="doc.status === 'pending'"
        class="text-xs btn-primary py-1 px-3"
        :disabled="store.processingIds.has(doc.id)"
        @click="$emit('process', doc.id)"
      >
        {{ store.processingIds.has(doc.id) ? '处理中...' : '处理' }}
      </button>
      <button
        v-if="doc.status === 'failed'"
        class="text-xs text-orange-600 hover:text-orange-800 py-1 px-3 border border-orange-300 rounded"
        :disabled="store.processingIds.has(doc.id)"
        @click="$emit('process', doc.id)"
      >
        {{ store.processingIds.has(doc.id) ? '重试中...' : '重试' }}
      </button>
      <button
        v-if="doc.status === 'completed'"
        class="text-xs text-primary-600 hover:text-primary-800"
        @click="$emit('viewChunks', doc.id)"
      >
        片段
      </button>
      <button
        class="text-xs text-red-600 hover:text-red-800 p-1"
        @click="$emit('delete', doc.id)"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  </div>
</template>
