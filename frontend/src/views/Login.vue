<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const isRegister = ref(false)
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  if (!username.value.trim() || !password.value.trim()) {
    error.value = '请填写所有必填项'
    return
  }

  loading.value = true
  try {
    if (isRegister.value) {
      if (!email.value.trim()) {
        error.value = '注册时邮箱为必填项'
        loading.value = false
        return
      }
      await auth.register(username.value, email.value, password.value)
    } else {
      await auth.login(username.value, password.value)
    }
    router.push({ name: 'Chat' })
  } catch (err) {
    error.value = err.response?.data?.detail || '认证失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-100">
    <div class="card w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">企业 RAG</h1>
        <p class="text-sm text-gray-500 mt-1">智能知识库</p>
      </div>

      <!-- Toggle -->
      <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
        <button
          class="flex-1 py-2 text-sm rounded-md transition-colors"
          :class="!isRegister ? 'bg-white shadow text-gray-900' : 'text-gray-500'"
          @click="isRegister = false; error = ''"
        >
          登录
        </button>
        <button
          class="flex-1 py-2 text-sm rounded-md transition-colors"
          :class="isRegister ? 'bg-white shadow text-gray-900' : 'text-gray-500'"
          @click="isRegister = true; error = ''"
        >
          注册
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input
            v-model="username"
            type="text"
            class="input-field"
            placeholder="请输入用户名"
            autofocus
          />
        </div>
        <div v-if="isRegister">
          <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
          <input
            v-model="email"
            type="email"
            class="input-field"
            placeholder="请输入邮箱"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
          <input
            v-model="password"
            type="password"
            class="input-field"
            placeholder="请输入密码"
          />
        </div>
        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        <button type="submit" class="btn-primary w-full py-3 text-base" :disabled="loading">
          {{ loading ? '请稍候...' : (isRegister ? '创建账号' : '登录') }}
        </button>
      </form>
    </div>
  </div>
</template>
