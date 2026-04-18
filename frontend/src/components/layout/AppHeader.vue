<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'
import { Bell, Menu, LogOut, User } from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'

const emit = defineEmits(['toggle-sidebar'])

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const notifStore = useNotificacionesStore()

const pageTitle = computed(() => {
  const titles = {
    dashboard: 'Dashboard',
    pipeline: 'Pipeline Comercial',
    deals: 'Deals',
    'deal-detail': 'Detalle del Deal',
    'deal-create': 'Nuevo Deal',
    'deal-edit': 'Editar Deal',
    clientes: 'Clientes',
    'cliente-detail': 'Detalle del Cliente',
    documentos: 'Documentos',
    tareas: 'Tareas',
    notificaciones: 'Notificaciones',
    'admin-usuarios': 'Gestión de Usuarios',
  }
  return titles[route.name] || 'EnerFlow'
})

const userName = computed(() => {
  const u = auth.user
  if (!u) return 'Usuario'
  if (u.first_name) return `${u.first_name} ${u.last_name || ''}`.trim()
  return u.username || 'Usuario'
})

const userInitials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  if (u.first_name && u.last_name) return `${u.first_name[0]}${u.last_name[0]}`.toUpperCase()
  if (u.username) return u.username.slice(0, 2).toUpperCase()
  return '?'
})

const userMenuItems = computed(() => [
  {
    label: 'Mi Perfil',
    icon: User,
    action: () => {},
  },
  { separator: true },
  {
    label: 'Cerrar Sesión',
    icon: LogOut,
    destructive: true,
    action: () => {
      auth.logout()
      router.push('/login')
    },
  },
])
</script>

<template>
  <header class="flex h-15 items-center gap-4 border-b bg-background px-6 shrink-0" style="height:60px;">
    <!-- Mobile hamburger -->
    <button
      class="lg:hidden text-muted-foreground hover:text-foreground"
      @click="emit('toggle-sidebar')"
    >
      <Menu class="h-5 w-5" />
    </button>

    <!-- Page title -->
    <h1 class="text-base font-semibold text-foreground flex-1">{{ pageTitle }}</h1>

    <!-- Right side -->
    <div class="flex items-center gap-2">
      <!-- Notifications bell -->
      <button
        class="relative flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
        @click="router.push('/notificaciones')"
      >
        <Bell class="h-5 w-5" />
        <span
          v-if="notifStore.count > 0"
          class="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-white"
        >
          {{ notifStore.count > 9 ? '9+' : notifStore.count }}
        </span>
      </button>

      <!-- User avatar dropdown -->
      <DropdownMenu :items="userMenuItems" align="right">
        <template #trigger>
          <button class="flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-accent transition-colors">
            <Avatar :fallback="userInitials" size="sm" />
            <span class="hidden md:block text-sm font-medium text-foreground max-w-[120px] truncate">
              {{ userName }}
            </span>
          </button>
        </template>
      </DropdownMenu>
    </div>
  </header>
</template>
