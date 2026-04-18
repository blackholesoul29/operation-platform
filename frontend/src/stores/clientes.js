import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/lib/api'

export const useClientesStore = defineStore('clientes', () => {
  const clientes = ref([])
  const currentCliente = ref(null)
  const loading = ref(false)
  const total = ref(0)

  async function fetchClientes(params = {}) {
    loading.value = true
    try {
      const { data } = await api.get('/clientes/', { params })
      clientes.value = data.results || data
      total.value = data.count || clientes.value.length
    } finally {
      loading.value = false
    }
  }

  async function fetchCliente(id) {
    loading.value = true
    try {
      const { data } = await api.get(`/clientes/${id}/`)
      currentCliente.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function createCliente(payload) {
    const { data } = await api.post('/clientes/', payload)
    clientes.value.unshift(data)
    total.value += 1
    return data
  }

  async function updateCliente(id, payload) {
    const { data } = await api.patch(`/clientes/${id}/`, payload)
    if (currentCliente.value?.id === id) currentCliente.value = data
    const idx = clientes.value.findIndex((c) => c.id === id)
    if (idx !== -1) clientes.value[idx] = data
    return data
  }

  async function deleteCliente(id) {
    await api.delete(`/clientes/${id}/`)
    clientes.value = clientes.value.filter((c) => c.id !== id)
    total.value -= 1
  }

  async function addContacto(clienteId, payload) {
    const { data } = await api.post(`/clientes/${clienteId}/contactos/`, payload)
    if (currentCliente.value?.id === clienteId) {
      if (!currentCliente.value.contactos) currentCliente.value.contactos = []
      currentCliente.value.contactos.push(data)
    }
    return data
  }

  async function updateContacto(clienteId, contactoId, payload) {
    const { data } = await api.patch(`/clientes/${clienteId}/contactos/${contactoId}/`, payload)
    if (currentCliente.value?.id === clienteId) {
      const idx = currentCliente.value.contactos?.findIndex((c) => c.id === contactoId)
      if (idx !== -1) currentCliente.value.contactos[idx] = data
    }
    return data
  }

  async function deleteContacto(clienteId, contactoId) {
    await api.delete(`/clientes/${clienteId}/contactos/${contactoId}/`)
    if (currentCliente.value?.id === clienteId) {
      currentCliente.value.contactos = currentCliente.value.contactos?.filter(
        (c) => c.id !== contactoId
      )
    }
  }

  return {
    clientes,
    currentCliente,
    loading,
    total,
    fetchClientes,
    fetchCliente,
    createCliente,
    updateCliente,
    deleteCliente,
    addContacto,
    updateContacto,
    deleteContacto,
  }
})
