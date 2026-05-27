<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useConversationsStore } from '../stores/conversations'
import { useChatStore } from '../stores/chat'

const router = useRouter()
const route = useRoute()
const convStore = useConversationsStore()
const chatStore = useChatStore()
const collapsed = ref(false)
const selectedIds = ref(new Set())
const selectMode = ref(false)

const allSelected = computed(() =>
  convStore.conversations.length > 0 && convStore.conversations.every((c) => selectedIds.value.has(c.id))
)

const selectedCount = computed(() => selectedIds.value.size)

onMounted(() => {
  convStore.fetchConversations()
})

function toggleSelectMode() {
  selectMode.value = !selectMode.value
  if (!selectMode.value) {
    selectedIds.value.clear()
  }
}

function toggleSelect(id) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value.clear()
  } else {
    convStore.conversations.forEach((c) => selectedIds.value.add(c.id))
  }
}

function newChat() {
  chatStore.clearMessages()
  convStore.clearCurrent()
  router.push({ name: 'Chat' })
}

async function openConversation(id) {
  if (selectMode.value) {
    toggleSelect(id)
    return
  }
  const data = await convStore.fetchConversation(id)
  chatStore.loadMessages(data.messages)
  router.push({ name: 'ChatConversation', params: { conversationId: id } })
}

async function deleteConversation(id, e) {
  e.stopPropagation()
  if (!confirm('确定删除此对话？')) return
  await convStore.removeConversation(id)
  selectedIds.value.delete(id)
  if (route.params.conversationId === String(id)) {
    newChat()
  }
}

async function batchDelete() {
  if (!selectedCount.value) return
  if (!confirm(`确定删除选中的 ${selectedCount.value} 条对话？`)) return
  const ids = [...selectedIds.value]
  const deletedCurrent = ids.includes(Number(route.params.conversationId))
  await convStore.removeConversations(ids)
  selectedIds.value.clear()
  if (deletedCurrent) newChat()
}

async function clearAll() {
  if (!convStore.conversations.length) return
  if (!confirm(`确定清空全部 ${convStore.conversations.length} 条对话记录？`)) return
  const ids = convStore.conversations.map((c) => c.id)
  await convStore.removeConversations(ids)
  selectedIds.value.clear()
  newChat()
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  if (diff < 86400000 && d.getDate() === now.getDate()) {
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<template>
  <aside
    class="flex flex-col bg-gray-900 text-gray-100 transition-all duration-300"
    :class="collapsed ? 'w-16' : 'w-72'"
  >
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-700">
      <h1 v-if="!collapsed" class="text-sm font-semibold truncate">RAG 知识库</h1>
      <button
        class="p-1 rounded hover:bg-gray-700"
        @click="collapsed = !collapsed"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            v-if="collapsed"
            stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M13 5l7 7-7 7M5 5l7 7-7 7"
          />
          <path
            v-else
            stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
          />
        </svg>
      </button>
    </div>

    <!-- New Chat -->
    <div class="p-3">
      <button
        class="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 transition-colors text-sm"
        @click="newChat"
      >
        <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span v-if="!collapsed">新对话</span>
      </button>
    </div>

    <!-- Navigation -->
    <nav v-if="!collapsed" class="px-3 space-y-1">
      <router-link
        :to="{ name: 'Documents' }"
        class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm hover:bg-gray-800 transition-colors"
        active-class="bg-gray-800"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
          />
        </svg>
        文档
      </router-link>
    </nav>

    <!-- Conversations -->
    <div v-if="!collapsed" class="flex-1 overflow-y-auto mt-3 px-3">
      <div class="flex items-center justify-between mb-2 px-3">
        <p class="text-xs text-gray-500 uppercase tracking-wider">历史记录</p>
        <div class="flex items-center gap-1">
          <button
            v-if="!selectMode && convStore.conversations.length > 0"
            class="text-xs text-gray-500 hover:text-gray-300 px-1.5 py-0.5 rounded hover:bg-gray-800"
            @click="toggleSelectMode"
          >
            管理
          </button>
          <button
            v-if="selectMode"
            class="text-xs text-gray-400 hover:text-gray-200 px-1.5 py-0.5 rounded hover:bg-gray-800"
            @click="toggleSelectMode"
          >
            取消
          </button>
        </div>
      </div>

      <!-- Select mode toolbar -->
      <div v-if="selectMode" class="flex items-center gap-2 mb-2 px-3">
        <label class="flex items-center gap-1.5 cursor-pointer">
          <input
            type="checkbox"
            :checked="allSelected"
            class="w-3.5 h-3.5 rounded border-gray-600 text-primary-600 focus:ring-primary-500 bg-gray-700"
            @change="toggleSelectAll"
          />
          <span class="text-xs text-gray-400">全选</span>
        </label>
        <button
          v-if="selectedCount > 0"
          class="text-xs text-red-400 hover:text-red-300 px-1.5 py-0.5 rounded hover:bg-gray-800"
          @click="batchDelete"
        >
          删除 ({{ selectedCount }})
        </button>
        <button
          class="text-xs text-gray-500 hover:text-gray-300 px-1.5 py-0.5 rounded hover:bg-gray-800 ml-auto"
          @click="clearAll"
        >
          清空
        </button>
      </div>

      <div class="space-y-0.5">
        <div
          v-for="conv in convStore.conversations"
          :key="conv.id"
          class="group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-800 transition-colors"
          :class="{ 'bg-gray-800': route.params.conversationId === String(conv.id) }"
          @click="openConversation(conv.id)"
        >
          <!-- Checkbox in select mode -->
          <input
            v-if="selectMode"
            type="checkbox"
            :checked="selectedIds.has(conv.id)"
            class="w-3.5 h-3.5 rounded border-gray-600 text-primary-600 focus:ring-primary-500 bg-gray-700 flex-shrink-0"
            @click.stop
            @change="toggleSelect(conv.id)"
          />
          <svg v-else class="w-4 h-4 text-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
          <div class="flex-1 min-w-0">
            <p class="text-sm truncate">{{ conv.title }}</p>
            <p class="text-xs text-gray-500">{{ formatDate(conv.updated_at) }}</p>
          </div>
          <button
            v-if="!selectMode"
            class="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-gray-700 transition-opacity"
            @click="deleteConversation(conv.id, $event)"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div v-if="!collapsed" class="p-4 border-t border-gray-700 text-xs text-gray-500">
      企业 RAG v0.1
    </div>
  </aside>
</template>
