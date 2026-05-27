import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('rag_token') || '')
  const username = ref(localStorage.getItem('rag_username') || '')
  const userId = ref(Number(localStorage.getItem('rag_user_id')) || 0)

  const isLoggedIn = computed(() => !!token.value)

  async function login(name, password) {
    const { data } = await api.post('/auth/login', { username: name, password })
    token.value = data.access_token
    username.value = name
    localStorage.setItem('rag_token', data.access_token)
    localStorage.setItem('rag_username', name)
    // Fetch user info
    await fetchMe()
  }

  async function register(name, email, password) {
    await api.post('/auth/register', { username: name, email, password })
    await login(name, password)
  }

  async function fetchMe() {
    try {
      const { data } = await api.get('/auth/me')
      userId.value = data.id
      username.value = data.username
      localStorage.setItem('rag_user_id', data.id)
      localStorage.setItem('rag_username', data.username)
    } catch {
      // token might be expired
      logout()
    }
  }

  function logout() {
    token.value = ''
    username.value = ''
    userId.value = 0
    localStorage.removeItem('rag_token')
    localStorage.removeItem('rag_username')
    localStorage.removeItem('rag_user_id')
  }

  // Initialize: check if stored token is valid
  if (token.value) {
    fetchMe()
  }

  return { token, username, userId, isLoggedIn, login, register, logout, fetchMe }
})
