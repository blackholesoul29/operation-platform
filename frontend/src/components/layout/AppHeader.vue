<script setup>
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const navItems = [
  { label: 'Dashboard',                       to: '/',               names: ['dashboard'] },
  { label: 'Deals',                           to: '/deals',          names: ['deals', 'deal-detail', 'deal-create', 'deal-edit'] },
  { label: 'Creación de clientes',            to: '/clientes/nuevo', names: ['cliente-crear'] },
  { label: 'Listado de clientes y servicios', to: '/clientes',       names: ['clientes', 'cliente-detail'] },
]

function isActive(item) {
  return item.names.includes(route.name)
}
</script>

<template>
  <header class="bg-background border-b shrink-0">
    <!-- Horizontal nav -->
    <nav class="flex items-center gap-0 px-6 overflow-x-auto">
      <button
        v-for="item in navItems"
        :key="item.to"
        :class="[
          'px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors',
          isActive(item)
            ? 'border-primary text-primary'
            : 'border-transparent text-muted-foreground hover:text-foreground hover:border-slate-300',
        ]"
        @click="router.push(item.to)"
      >
        {{ item.label }}
      </button>
    </nav>
  </header>
</template>
