import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/lib/api'

export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref({
    deals_activos: 0,
    deals_cerrados_mes: 0,
    valor_pipeline_total: 0,
    tasa_conversion: 0,
    deals_por_etapa: {},
    deals_por_servicio: {},
  })
  const pipeline = ref({})
  const loading = ref(false)

  async function fetchStats() {
    loading.value = true
    try {
      const { data } = await api.get('/dashboard/stats/')
      stats.value = data
    } catch {
      // use defaults
    } finally {
      loading.value = false
    }
  }

  async function fetchPipeline() {
    try {
      const { data } = await api.get('/dashboard/pipeline/')
      pipeline.value = data
    } catch {
      // silently fail
    }
  }

  return {
    stats,
    pipeline,
    loading,
    fetchStats,
    fetchPipeline,
  }
})
