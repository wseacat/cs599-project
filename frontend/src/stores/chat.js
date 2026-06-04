import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendChat } from '../services/api'
import { streamChat } from '../services/sse'
import { useConversationsStore } from './conversations'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const streamingText = ref('')
  const isStreaming = ref(false)
  const currentAgent = ref('')
  const workflowProgress = ref([])
  const error = ref(null)
  let abortController = null

  function addUserMessage(content) {
    messages.value.push({
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    })
  }

  function addAssistantMessage(content, citations, workflowTrace, messageId) {
    messages.value.push({
      role: 'assistant',
      content,
      citations: citations || [],
      workflow_trace: workflowTrace || [],
      message_id: messageId,
      created_at: new Date().toISOString(),
    })
  }

  async function sendMessage(content, conversationId, useSSE = true) {
    error.value = null
    addUserMessage(content)

    if (useSSE) {
      return sendStreaming(content, conversationId)
    }
    return sendNonStreaming(content, conversationId)
  }

  async function sendNonStreaming(content, conversationId) {
    isStreaming.value = true
    try {
      const { data } = await sendChat(content, conversationId)
      addAssistantMessage(data.answer, data.citations, data.workflow_trace, data.message_id)
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isStreaming.value = false
    }
  }

  function sendStreaming(content, conversationId) {
    isStreaming.value = true
    streamingText.value = ''
    currentAgent.value = ''
    workflowProgress.value = []

    return new Promise((resolve, reject) => {
      abortController = streamChat(content, conversationId, {
        onProgress(progressData) {
          currentAgent.value = progressData.agent || ''
          workflowProgress.value.push(progressData)

          // Update streaming text based on agent progress
          if (progressData.agent === 'answer') {
            streamingText.value = '正在生成答案...'
          } else if (progressData.agent === 'planner') {
            streamingText.value = '正在分析问题...'
          } else if (progressData.agent === 'query_agent') {
            streamingText.value = '正在优化查询...'
          } else if (progressData.agent === 'retriever') {
            streamingText.value = `正在检索文档 (${progressData.doc_count || 0} 个结果)...`
          } else if (progressData.agent === 'rerank') {
            streamingText.value = '正在重排序...'
          } else if (progressData.agent === 'reflection') {
            streamingText.value = progressData.passed ? '检索质量良好' : '正在重试检索...'
          }
        },
        onToken(tokenData) {
          streamingText.value = tokenData.text || ''
        },
        onFinal(finalData) {
          isStreaming.value = false
          streamingText.value = ''
          currentAgent.value = ''
          addAssistantMessage(
            finalData.answer,
            finalData.citations,
            finalData.workflow_trace,
            finalData.message_id,
          )
          // Update conversations store
          const convStore = useConversationsStore()
          convStore.fetchConversations()
          resolve(finalData)
        },
        onError(err) {
          isStreaming.value = false
          streamingText.value = ''
          currentAgent.value = ''
          error.value = err.message
          reject(err)
        },
      })
    })
  }

  function cancelStream() {
    abortController?.abort()
    isStreaming.value = false
    streamingText.value = ''
    currentAgent.value = ''
  }

  function loadMessages(msgs) {
    messages.value = msgs.map((m) => {
      let citations = []
      try {
        citations = m.citations_json ? JSON.parse(m.citations_json) : []
      } catch {
        citations = []
      }
      return { ...m, citations }
    })
  }

  function clearMessages() {
    messages.value = []
    streamingText.value = ''
    currentAgent.value = ''
    workflowProgress.value = []
    error.value = null
  }

  return {
    messages,
    streamingText,
    isStreaming,
    currentAgent,
    workflowProgress,
    error,
    sendMessage,
    cancelStream,
    loadMessages,
    clearMessages,
  }
})
