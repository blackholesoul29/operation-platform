<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Zap,
  LayoutDashboard,
  Kanban,
  Briefcase,
  Building2,
  FolderOpen,
  CheckSquare,
  Users,
  LogOut,
  X,
  Activity,
  Receipt,
} from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'

const props = defineProps({
  mobileOpen: { type: Boolean, default: false },
})

const emit = defineEmits(['close'])

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const navItems = computed(() => {
  const items = [
    { label: 'Dashboard', icon: LayoutDashboard, to: '/', name: 'dashboard' },
    { label: 'Pipeline', icon: Kanban, to: '/pipeline', name: 'pipeline' },
    { label: 'Deals', icon: Briefcase, to: '/deals', name: 'deals' },
    { label: 'Clientes', icon: Building2, to: '/clientes', name: 'clientes' },
    { separator: true },
    { label: 'Proyectos', icon: Zap, to: '/proyectos', name: 'proyectos' },
    { label: 'CGM', icon: Activity, to: '/cgm', name: 'cgm' },
    { label: 'Liquidaciones', icon: Receipt, to: '/liquidaciones', name: 'liquidaciones' },
    { separator: true },
    { label: 'Documentos', icon: FolderOpen, to: '/documentos', name: 'documentos' },
    { label: 'Tareas', icon: CheckSquare, to: '/tareas', name: 'tareas' },
  ]

  if (auth.isAdmin) {
    items.push({ separator: true })
    items.push({ label: 'Usuarios', icon: Users, to: '/admin/usuarios', name: 'admin-usuarios' })
  }

  return items
})

function isActive(item) {
  if (item.name === 'dashboard') return route.path === '/'
  return route.path.startsWith(item.to)
}

function navigate(to) {
  router.push(to)
  emit('close')
}

function logout() {
  auth.logout()
  router.push('/login')
}

const userInitials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  if (u.first_name && u.last_name) return `${u.first_name[0]}${u.last_name[0]}`.toUpperCase()
  if (u.username) return u.username.slice(0, 2).toUpperCase()
  return '?'
})

const userName = computed(() => {
  const u = auth.user
  if (!u) return 'Usuario'
  if (u.first_name) return `${u.first_name} ${u.last_name || ''}`.trim()
  return u.username || 'Usuario'
})

const userRole = computed(() => {
  const roles = {
    admin: 'Administrador',
    manager_comercial: 'Manager Comercial',
    comercial: 'Comercial',
    operaciones: 'Operaciones',
    viewer: 'Visualizador',
  }
  return roles[auth.user?.role] || auth.user?.role || ''
})
</script>

<template>
  <!-- Desktop sidebar always visible, mobile sidebar toggleable -->
  <aside
    :class="[
      'fixed lg:static inset-y-0 left-0 z-30 flex h-full w-60 flex-col bg-slate-800 text-white transition-transform duration-300 ease-in-out',
      mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
    ]"
  >
    <!-- Logo -->
    <div class="flex items-center gap-3 px-4 py-5 border-b border-slate-700">
      <div class="flex items-center justify-center h-9 w-9 rounded-lg bg-primary">
        <Zap class="h-5 w-5 text-white" />
      </div>
      <span class="text-xl font-bold tracking-tight text-white">Unergy</span>
      <button class="ml-auto lg:hidden text-slate-400 hover:text-white" @click="emit('close')">
        <X class="h-5 w-5" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-4 px-2">
      <ul class="space-y-0.5">
        <template v-for="item in navItems" :key="item.label || 'sep'">
          <li v-if="item.separator" class="my-2">
            <div class="h-px bg-slate-700" />
          </li>
          <li v-else>
            <button
              :class="[
                'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all',
                isActive(item)
                  ? 'bg-slate-700 text-white shadow-sm'
                  : 'text-slate-400 hover:bg-slate-700/60 hover:text-white',
              ]"
              @click="navigate(item.to)"
            >
              <component :is="item.icon" class="h-5 w-5 flex-shrink-0" />
              <span>{{ item.label }}</span>
            </button>
          </li>
        </template>
      </ul>
    </nav>

    <!-- User profile -->
    <div class="border-t border-slate-700 p-3">
      <div class="flex items-center gap-3 rounded-lg p-2">
        <Avatar :fallback="userInitials" size="sm" class="flex-shrink-0" />
        <div class="min-w-0 flex-1">
          <p class="text-sm font-medium text-white truncate">{{ userName }}</p>
          <p class="text-xs text-slate-400 truncate">{{ userRole }}</p>
        </div>
        <button
          class="text-slate-400 hover:text-white transition-colors p-1 rounded"
          title="Cerrar sesión"
          @click="logout"
        >
          <LogOut class="h-4 w-4" />
        </button>
      </div>
    </div>
  </aside>
</template>
