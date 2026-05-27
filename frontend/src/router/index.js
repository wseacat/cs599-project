import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Chat',
        component: () => import('../views/Chat.vue'),
      },
      {
        path: 'chat/:conversationId',
        name: 'ChatConversation',
        component: () => import('../views/Chat.vue'),
        props: true,
      },
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('../views/DocumentUpload.vue'),
      },
      {
        path: 'retrieval-debug/:messageId',
        name: 'RetrievalDebug',
        component: () => import('../views/RetrievalDebug.vue'),
        props: true,
      },
      {
        path: 'citations/:messageId',
        name: 'CitationSource',
        component: () => import('../views/CitationSource.vue'),
        props: true,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'Login' }
  }
  if (to.name === 'Login' && auth.isLoggedIn) {
    return { name: 'Chat' }
  }
})

export default router
