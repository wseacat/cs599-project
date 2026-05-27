<script setup>
defineProps({
  title: { type: String, required: true },
  icon: { type: String, default: '' },
  expanded: { type: Boolean, default: false },
})

defineEmits(['toggle'])
</script>

<template>
  <div class="border border-gray-200 rounded-lg overflow-hidden">
    <button
      class="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
      @click="$emit('toggle')"
    >
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium text-gray-700">{{ title }}</span>
      </div>
      <svg
        class="w-4 h-4 text-gray-500 transition-transform"
        :class="{ 'rotate-180': expanded }"
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    <div v-if="expanded" class="px-4 py-3 border-t border-gray-200">
      <slot />
    </div>
  </div>
</template>
