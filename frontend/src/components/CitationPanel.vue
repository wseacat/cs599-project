<script setup>
defineProps({
  citations: { type: Array, default: () => [] },
})
</script>

<template>
  <div v-if="citations.length" class="space-y-3">
    <h3 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
        />
      </svg>
      引用来源
    </h3>
    <div
      v-for="(cite, i) in citations"
      :key="i"
      class="bg-gray-50 rounded-lg p-3 border border-gray-200"
    >
      <div class="flex items-center gap-2 mb-1">
        <span class="text-xs font-medium text-primary-600 bg-primary-50 px-1.5 py-0.5 rounded">
          #{{ i + 1 }}
        </span>
        <span class="text-xs font-medium text-gray-700 truncate">
          {{ cite.filename || '文档' }}
        </span>
        <span v-if="cite.page" class="text-xs text-gray-500 ml-auto">
          第 {{ cite.page }} 页
        </span>
      </div>
      <p v-if="cite.snippet" class="text-xs text-gray-600 line-clamp-3">
        {{ cite.snippet }}
      </p>
    </div>
  </div>
</template>
