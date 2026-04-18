import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/lib/api'

export const useDocumentosStore = defineStore('documentos', () => {
  const documentos = ref([])
  const loading = ref(false)
  const total = ref(0)

  async function fetchDocumentos(params = {}) {
    loading.value = true
    try {
      const { data } = await api.get('/documentos/', { params })
      documentos.value = data.results || data
      total.value = data.count || documentos.value.length
    } finally {
      loading.value = false
    }
  }

  async function uploadDocumento(formData) {
    const { data } = await api.post('/documentos/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    documentos.value.unshift(data)
    total.value += 1
    return data
  }

  async function deleteDocumento(id) {
    await api.delete(`/documentos/${id}/`)
    documentos.value = documentos.value.filter((d) => d.id !== id)
    total.value -= 1
  }

  async function updateEstado(id, estado) {
    const { data } = await api.patch(`/documentos/${id}/`, { estado })
    const idx = documentos.value.findIndex((d) => d.id === id)
    if (idx !== -1) documentos.value[idx] = data
    return data
  }

  return {
    documentos,
    loading,
    total,
    fetchDocumentos,
    uploadDocumento,
    deleteDocumento,
    updateEstado,
  }
})
