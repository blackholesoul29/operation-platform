<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'

const authStore = useAuthStore()
const notifStore = useNotificacionesStore()
const sidebarOpen = ref(false)

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await authStore.fetchMe()
    await notifStore.fetchCount()
  }
})
</script>

<template>
  <div class="flex h-screen bg-background overflow-hidden">
    <!-- Mobile overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-20 bg-black/50 lg:hidden"
      @click="sidebarOpen = false"
    />

    <AppSidebar :mobile-open="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col overflow-hidden min-w-0">
      <AppHeader @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <main class="flex-1 overflow-y-auto p-6 bg-slate-50/50">
        <RouterView />
      </main>
    </div>
  </div>
</template>
