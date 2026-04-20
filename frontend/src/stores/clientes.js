import { defineStore } from 'pinia'
import { ref } from 'vue'
import { googleApi } from '@/lib/googleApi'

export const useClientesStore = defineStore('clientes', () => {
  const clientes = ref([])
  const loading = ref(false)
  const uploading = ref({})  // { 'clientId_fieldName': true }
  const error = ref(null)

  async function fetchClientes() {
    loading.value = true
    error.value = null
    try {
      const data = await googleApi.getClientes()
      clientes.value = Array.isArray(data) ? data : []
    } catch (e) {
      error.value = e.message
      clientes.value = []
    } finally {
      loading.value = false
    }
  }

  async function createCliente(payload) {
    const result = await googleApi.createCliente(payload)
    await fetchClientes()
    return result
  }

  async function updateCliente(id, payload) {
    await googleApi.updateCliente(id, payload)
    await fetchClientes()
  }

  async function deleteCliente(id) {
    await googleApi.deleteCliente(id)
    clientes.value = clientes.value.filter((c) => c.id !== id)
  }

  async function uploadFile(clientId, fieldName, file) {
    const key = `${clientId}_${fieldName}`
    uploading.value = { ...uploading.value, [key]: true }
    try {
      const result = await googleApi.uploadFile(clientId, fieldName, file)
      // Actualizar el campo en local sin re-fetch completo
      const idx = clientes.value.findIndex((c) => c.id === clientId)
      if (idx >= 0) {
        clientes.value[idx] = { ...clientes.value[idx], [`${fieldName}_url`]: result.fileUrl }
      }
      return result
    } finally {
      const u = { ...uploading.value }
      delete u[key]
      uploading.value = u
    }
  }

  function isUploading(clientId, fieldName) {
    return !!uploading.value[`${clientId}_${fieldName}`]
  }

  // Computed helpers
  const total = { get value() { return clientes.value.length } }

  return {
    clientes,
    loading,
    uploading,
    error,
    total,
    fetchClientes,
    createCliente,
    updateCliente,
    deleteCliente,
    uploadFile,
    isUploading,
  }
})
