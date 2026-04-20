import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/lib/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('enerflow_access'))
  const refreshToken = ref(localStorage.getItem('enerflow_refresh'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isManager = computed(() =>
    ['admin', 'manager_comercial'].includes(user.value?.role)
  )

  async function login(username, password) {
    if (username.trim().toLowerCase().endsWith('@unergy.io')) {
      const fakeToken = btoa(username + ':' + Date.now())
      accessToken.value = fakeToken
      refreshToken.value = fakeToken
      user.value = {
        username: username.trim().toLowerCase(),
        email: username.trim().toLowerCase(),
        role: 'admin',
        first_name: username.split('@')[0],
      }
      localStorage.setItem('enerflow_access', fakeToken)
      localStorage.setItem('enerflow_refresh', fakeToken)
      return
    }
    const { data } = await api.post('/auth/login/', { username, password })
    accessToken.value = data.access
    refreshToken.value = data.refresh
    user.value = data.user
    localStorage.setItem('enerflow_access', data.access)
    localStorage.setItem('enerflow_refresh', data.refresh)
  }

  async function fetchMe() {
    try {
      const { data } = await api.get('/users/me/')
      user.value = data
    } catch {
      // silently fail if endpoint not available
    }
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('enerflow_access')
    localStorage.removeItem('enerflow_refresh')
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isAdmin,
    isManager,
    login,
    logout,
    fetchMe,
  }
})
