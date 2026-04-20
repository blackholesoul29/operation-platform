import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)

  const isAuthenticated = computed(() => true)
  const isAdmin = computed(() => true)
  const isManager = computed(() => true)

  async function fetchMe() {}

  return {
    user,
    isAuthenticated,
    isAdmin,
    isManager,
    fetchMe,
  }
})
