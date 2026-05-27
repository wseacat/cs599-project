import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// Attach JWT token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('rag_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 responses globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('rag_token')
      localStorage.removeItem('rag_username')
      localStorage.removeItem('rag_user_id')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

// Documents
export const uploadDocument = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const processDocument = (documentId) =>
  api.post(`/documents/${documentId}/process`)

export const listDocuments = () => api.get('/documents/')

export const getDocumentChunks = (documentId) =>
  api.get(`/documents/${documentId}/chunks`)

export const deleteDocument = (documentId) =>
  api.delete(`/documents/${documentId}`)

// Chat
export const sendChat = (message, conversationId) =>
  api.post('/chat', { message, conversation_id: conversationId })

// Conversations
export const listConversations = () => api.get('/conversations/')

export const getConversation = (conversationId) =>
  api.get(`/conversations/${conversationId}`)

export const deleteConversation = (conversationId) =>
  api.delete(`/conversations/${conversationId}`)

// Retrieval Debug
export const getRetrievalDebug = (messageId) =>
  api.get(`/retrieval/debug/${messageId}`)

// Health
export const checkHealth = () => api.get('/health')

export default api
