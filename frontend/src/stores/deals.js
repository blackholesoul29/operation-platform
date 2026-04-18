import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/lib/api'

export const useDealsStore = defineStore('deals', () => {
  const deals = ref([])
  const pipeline = ref({})
  const currentDeal = ref(null)
  const loading = ref(false)
  const total = ref(0)

  async function fetchDeals(params = {}) {
    loading.value = true
    try {
      const { data } = await api.get('/deals/', { params })
      deals.value = data.results || data
      total.value = data.count || deals.value.length
    } finally {
      loading.value = false
    }
  }

  async function fetchPipeline() {
    loading.value = true
    try {
      const { data } = await api.get('/dashboard/pipeline/')
      pipeline.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchDeal(id) {
    loading.value = true
    try {
      const { data } = await api.get(`/deals/${id}/`)
      currentDeal.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function createDeal(payload) {
    const { data } = await api.post('/deals/', payload)
    return data
  }

  async function updateDeal(id, payload) {
    const { data } = await api.patch(`/deals/${id}/`, payload)
    if (currentDeal.value?.id === id) currentDeal.value = data
    const idx = deals.value.findIndex((d) => d.id === id)
    if (idx !== -1) deals.value[idx] = data
    return data
  }

  async function cambiarEtapa(id, payload) {
    const { data } = await api.post(`/deals/${id}/cambiar-etapa/`, payload)
    if (currentDeal.value?.id === id) currentDeal.value = data
    const idx = deals.value.findIndex((d) => d.id === id)
    if (idx !== -1) deals.value[idx] = data
    return data
  }

  async function addActividad(dealId, payload) {
    const { data } = await api.post(`/deals/${dealId}/actividades/`, payload)
    if (currentDeal.value?.id === dealId) {
      if (!currentDeal.value.actividades) currentDeal.value.actividades = []
      currentDeal.value.actividades.unshift(data)
    }
    return data
  }

  async function deleteDeal(id) {
    await api.delete(`/deals/${id}/`)
    deals.value = deals.value.filter((d) => d.id !== id)
  }

  return {
    deals,
    pipeline,
    currentDeal,
    loading,
    total,
    fetchDeals,
    fetchPipeline,
    fetchDeal,
    createDeal,
    updateDeal,
    cambiarEtapa,
    addActividad,
    deleteDeal,
  }
})
