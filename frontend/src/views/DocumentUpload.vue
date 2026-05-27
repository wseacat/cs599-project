<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDocumentsStore } from '../stores/documents'
import DocumentCard from '../components/DocumentCard.vue'

const store = useDocumentsStore()
const dragOver = ref(false)
const fileInput = ref(null)
const chunksModal = ref({ show: false, chunks: [], filename: '' })
const selectedIds = ref(new Set())

const allSelected = computed(() =>
  store.documents.length > 0 && store.documents.every((d) => selectedIds.value.has(d.id))
)

const someSelected = computed(() =>
  selectedIds.value.size > 0 && !allSelected.value
)

const selectedCount = computed(() => selectedIds.value.size)

onMounted(() => {
  store.fetchDocuments()
})

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
    store.documents.forEach((d) => selectedIds.value.add(d.id))
  }
}

function clearSelection() {
  selectedIds.value.clear()
}

function handleDrop(e) {
  dragOver.value = false
  const files = Array.from(e.dataTransfer.files)
  files.forEach(uploadFile)
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files)
  files.forEach(uploadFile)
  e.target.value = ''
}

async function uploadFile(file) {
  const allowed = ['.pdf', '.docx', '.txt', '.md']
  const ext = '.' + file.name.split('.').pop().toLowerCase()
  if (!allowed.includes(ext)) {
    alert(`不支持的文件类型：${ext}，支持：${allowed.join(', ')}`)
    return
  }
  try {
    const doc = await store.upload(file)
    await store.processDocument(doc.id)
  } catch (err) {
    console.error('Upload failed:', err)
  }
}

async function handleProcess(documentId) {
  try {
    await store.processDocument(documentId)
  } catch (err) {
    console.error('Process failed:', err)
  }
}

async function handleDelete(documentId) {
  if (!confirm('确定删除此文档？此操作不可撤销。')) return
  try {
    await store.removeDocument(documentId)
    selectedIds.value.delete(documentId)
  } catch (err) {
    console.error('Delete failed:', err)
  }
}

async function handleBatchDelete() {
  if (!selectedCount.value) return
  if (!confirm(`确定删除选中的 ${selectedCount.value} 份文档？此操作不可撤销。`)) return
  try {
    await store.removeDocuments([...selectedIds.value])
    selectedIds.value.clear()
  } catch (err) {
    console.error('Batch delete failed:', err)
  }
}

async function handleViewChunks(documentId) {
  try {
    const chunks = await store.getChunks(documentId)
    const doc = store.documents.find((d) => d.id === documentId)
    chunksModal.value = { show: true, chunks, filename: doc?.filename || '' }
  } catch (err) {
    console.error('Failed to load chunks:', err)
  }
}
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="max-w-4xl mx-auto px-6 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">文档管理</h1>

      <!-- Upload area -->
      <div
        class="border-2 border-dashed rounded-xl p-8 text-center mb-8 transition-colors"
        :class="dragOver ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-gray-50'"
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        @drop.prevent="handleDrop"
      >
        <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <p class="text-gray-600 mb-2">
          拖拽文件到此处，或
          <button class="text-primary-600 hover:text-primary-700 font-medium" @click="fileInput.click()">
            点击选择
          </button>
        </p>
        <p class="text-xs text-gray-400">支持 PDF、DOCX、TXT、MD 格式</p>
        <input
          ref="fileInput"
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md"
          class="hidden"
          @change="handleFileSelect"
        />
      </div>

      <!-- Loading -->
      <div v-if="store.loading" class="text-center py-8">
        <div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto" />
      </div>

      <!-- Document list -->
      <div v-else-if="store.documents.length" class="space-y-3">
        <!-- Toolbar -->
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-3">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                :checked="allSelected"
                class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                @change="toggleSelectAll"
              />
              <span class="text-sm text-gray-600">全选</span>
            </label>
            <span class="text-sm text-gray-500">共 {{ store.total }} 份文档</span>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="selectedCount > 0"
              class="text-sm text-red-600 hover:text-red-800 px-3 py-1.5 border border-red-300 rounded-lg hover:bg-red-50 transition-colors flex items-center gap-1"
              @click="handleBatchDelete"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              删除选中 ({{ selectedCount }})
            </button>
            <button
              v-if="selectedCount > 0"
              class="text-sm text-gray-500 hover:text-gray-700 px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              @click="clearSelection"
            >
              取消选择
            </button>
          </div>
        </div>

        <DocumentCard
          v-for="doc in store.documents"
          :key="doc.id"
          :doc="doc"
          :selected="selectedIds.has(doc.id)"
          @process="handleProcess"
          @delete="handleDelete"
          @view-chunks="handleViewChunks"
          @toggle-select="toggleSelect"
        />
      </div>

      <!-- Empty state -->
      <div v-else class="text-center py-12 text-gray-500">
        <p class="text-lg">暂无文档</p>
        <p class="text-sm mt-1">上传文档开始构建您的知识库</p>
      </div>
    </div>

    <!-- Chunks modal -->
    <div v-if="chunksModal.show" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[80vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-semibold">文档片段 — {{ chunksModal.filename }}</h2>
          <button class="text-gray-400 hover:text-gray-600" @click="chunksModal.show = false">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6 space-y-3">
          <div
            v-for="chunk in chunksModal.chunks"
            :key="chunk.id"
            class="bg-gray-50 rounded-lg p-4 border border-gray-200"
          >
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-0.5 rounded">
                #{{ chunk.chunk_index }}
              </span>
            </div>
            <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ chunk.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
