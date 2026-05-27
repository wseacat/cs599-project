import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '../services/api'

export const useConversationsStore = defineStore('conversations', () => {
  const conversations = ref([])
  const currentConversation = ref(null)
  const loading = ref(false)

  async function fetchConversations() {
    loading.value = true
    try {
      const { data } = await api.listConversations()
      conversations.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchConversation(id) {
    loading.value = true
    try {
      const { data } = await api.getConversation(id)
      currentConversation.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function removeConversation(id) {
    await api.deleteConversation(id)
    conversations.value = conversations.value.filter((c) => c.id !== id)
    if (currentConversation.value?.id === id) {
      currentConversation.value = null
    }
  }

  async function removeConversations(ids) {
    const results = await Promise.allSettled(
      ids.map((id) => api.deleteConversation(id))
    )
    const succeeded = new Set()
    results.forEach((r, i) => {
      if (r.status === 'fulfilled') succeeded.add(ids[i])
    })
    conversations.value = conversations.value.filter((c) => !succeeded.has(c.id))
    if (currentConversation.value && succeeded.has(currentConversation.value.id)) {
      currentConversation.value = null
    }
  }

  function setCurrent(conversation) {
    currentConversation.value = conversation
  }

  function clearCurrent() {
    currentConversation.value = null
  }

  return {
    conversations,
    currentConversation,
    loading,
    fetchConversations,
    fetchConversation,
    removeConversation,
    removeConversations,
    setCurrent,
    clearCurrent,
  }
})
