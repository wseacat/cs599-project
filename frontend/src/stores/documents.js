import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import * as api from '../services/api'

export const useDocumentsStore = defineStore('documents', () => {
  const documents = ref([])
  const total = ref(0)
  const loading = ref(false)
  const uploading = ref(false)
  const processingIds = reactive(new Set())

  async function fetchDocuments() {
    loading.value = true
    try {
      const { data } = await api.listDocuments()
      documents.value = data.documents
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function upload(file) {
    uploading.value = true
    try {
      const { data } = await api.uploadDocument(file)
      documents.value.unshift(data)
      total.value++
      return data
    } finally {
      uploading.value = false
    }
  }

  async function processDocument(documentId) {
    processingIds.add(documentId)
    try {
      const { data } = await api.processDocument(documentId)
      const doc = documents.value.find((d) => d.id === documentId)
      if (doc) {
        doc.status = data.error ? 'failed' : 'completed'
        doc.chunk_count = data.chunk_count || 0
      }
      return data
    } catch (err) {
      const doc = documents.value.find((d) => d.id === documentId)
      if (doc) doc.status = 'failed'
      throw err
    } finally {
      processingIds.delete(documentId)
    }
  }

  async function removeDocument(documentId) {
    await api.deleteDocument(documentId)
    documents.value = documents.value.filter((d) => d.id !== documentId)
    total.value--
  }

  async function removeDocuments(documentIds) {
    const results = await Promise.allSettled(
      documentIds.map((id) => api.deleteDocument(id))
    )
    const succeeded = new Set()
    results.forEach((r, i) => {
      if (r.status === 'fulfilled') succeeded.add(documentIds[i])
    })
    documents.value = documents.value.filter((d) => !succeeded.has(d.id))
    total.value -= succeeded.size
  }

  async function getChunks(documentId) {
    const { data } = await api.getDocumentChunks(documentId)
    return data
  }

  return {
    documents,
    total,
    loading,
    uploading,
    processingIds,
    fetchDocuments,
    upload,
    processDocument,
    removeDocument,
    removeDocuments,
    getChunks,
  }
})
