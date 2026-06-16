import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'highlight': ['highlight.js'],
          'vendor': ['vue', 'vue-router', 'pinia', 'axios'],
          'markdown': ['marked', 'dompurify'],
        },
      },
    },
    // Enable CSS code splitting
    cssCodeSplit: true,
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
  },
  // Enable preloading
  html: {
    cspNonce: undefined,
  },
})
