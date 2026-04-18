import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/lib/api'

export const useTareasStore = defineStore('tareas', () => {
  const tareas = ref([])
  const loading = ref(false)
  const total = ref(0)

  async function fetchTareas(params = {}) {
    loading.value = true
    try {
      const { data } = await api.get('/tareas/', { params })
      tareas.value = data.results || data
      total.value = data.count || tareas.value.length
    } finally {
      loading.value = false
    }
  }

  async function createTarea(payload) {
    const { data } = await api.post('/tareas/', payload)
    tareas.value.unshift(data)
    total.value += 1
    return data
  }

  async function updateTarea(id, payload) {
    const { data } = await api.patch(`/tareas/${id}/`, payload)
    const idx = tareas.value.findIndex((t) => t.id === id)
    if (idx !== -1) tareas.value[idx] = data
    return data
  }

  async function completarTarea(id) {
    const { data } = await api.post(`/tareas/${id}/completar/`)
    const idx = tareas.value.findIndex((t) => t.id === id)
    if (idx !== -1) tareas.value[idx] = data
    return data
  }

  async function deleteTarea(id) {
    await api.delete(`/tareas/${id}/`)
    tareas.value = tareas.value.filter((t) => t.id !== id)
    total.value -= 1
  }

  return {
    tareas,
    loading,
    total,
    fetchTareas,
    createTarea,
    updateTarea,
    completarTarea,
    deleteTarea,
  }
})
