import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/lib/api'

export const useNotificacionesStore = defineStore('notificaciones', () => {
  const notificaciones = ref([])
  const count = ref(0)
  const loading = ref(false)

  async function fetchNotificaciones(params = {}) {
    loading.value = true
    try {
      const { data } = await api.get('/notificaciones/', { params })
      notificaciones.value = data.results || data
    } finally {
      loading.value = false
    }
  }

  async function fetchCount() {
    try {
      const { data } = await api.get('/notificaciones/count/')
      count.value = data.count || 0
    } catch {
      // silently fail
    }
  }

  async function marcarLeida(id) {
    try {
      await api.post(`/notificaciones/${id}/marcar-leida/`)
      const idx = notificaciones.value.findIndex((n) => n.id === id)
      if (idx !== -1) {
        notificaciones.value[idx].leida = true
        if (count.value > 0) count.value -= 1
      }
    } catch {
      // silently fail
    }
  }

  async function marcarTodasLeidas() {
    try {
      await api.post('/notificaciones/marcar-todas-leidas/')
      notificaciones.value = notificaciones.value.map((n) => ({ ...n, leida: true }))
      count.value = 0
    } catch {
      // silently fail
    }
  }

  return {
    notificaciones,
    count,
    loading,
    fetchNotificaciones,
    fetchCount,
    marcarLeida,
    marcarTodasLeidas,
  }
})
