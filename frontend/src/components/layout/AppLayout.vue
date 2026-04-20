<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'
import AppHeader from './AppHeader.vue'

const authStore = useAuthStore()
const notifStore = useNotificacionesStore()

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await authStore.fetchMe()
    await notifStore.fetchCount()
  }
})
</script>

<template>
  <div class="flex flex-col h-screen bg-background overflow-hidden">
    <AppHeader />
    <main class="flex-1 overflow-y-auto p-6 bg-slate-50/50">
      <RouterView />
    </main>
  </div>
</template>
