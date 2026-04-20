<script setup>
import { ref, computed, onMounted } from 'vue'
import { useClientesStore } from '@/stores/clientes'
import { Search, ExternalLink, Briefcase } from 'lucide-vue-next'
import Input from '@/components/ui/Input.vue'
import Spinner from '@/components/ui/Spinner.vue'

const store = useClientesStore()
const search = ref('')

const ESTADOS = ['Originación', 'Negociación', 'Cierre']

const ESTADO_STYLE = {
  Originación: { header: 'bg-amber-50 border-amber-200', badge: 'bg-amber-100 text-amber-800', dot: 'bg-amber-400' },
  Negociación:  { header: 'bg-blue-50 border-blue-200',  badge: 'bg-blue-100 text-blue-800',  dot: 'bg-blue-400'  },
  Cierre:       { header: 'bg-green-50 border-green-200', badge: 'bg-green-100 text-green-800', dot: 'bg-green-400' },
}

const saving = ref(null) // clientId siendo guardado

onMounted(() => store.fetchClientes())

const filteredClientes = computed(() => {
  if (!search.value) return store.clientes
  const q = search.value.toLowerCase()
  return store.clientes.filter(c => c.nombre_comercial?.toLowerCase().includes(q))
})

function clientesByEstado(estado) {
  return filteredClientes.value.filter(c => (c.estado || 'Originación') === estado)
}

async function changeEstado(cliente, nuevoEstado) {
  if (cliente.estado === nuevoEstado) return
  saving.value = cliente.id
  try {
    await store.updateCliente(cliente.id, { estado: nuevoEstado })
  } finally {
    saving.value = null
  }
}
</script>

<template>
  <div class="space-y-4">

    <!-- Header -->
    <div class="flex items-center gap-3">
      <h1 class="text-2xl font-bold flex-1">Deals</h1>
      <span class="text-sm text-muted-foreground">{{ store.clientes.length }} cliente(s)</span>
    </div>

    <!-- Búsqueda -->
    <div class="relative max-w-xs">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input v-model="search" placeholder="Buscar cliente..." class="pl-9" />
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16"><Spinner size="lg" /></div>

    <!-- Error -->
    <div v-else-if="store.error" class="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
      {{ store.error }}
    </div>

    <!-- Kanban por estado -->
    <div v-else class="grid grid-cols-3 gap-4 items-start">
      <div
        v-for="estado in ESTADOS"
        :key="estado"
        class="rounded-xl border overflow-hidden"
        :class="ESTADO_STYLE[estado].header"
      >
        <!-- Cabecera columna -->
        <div class="px-4 py-3 border-b flex items-center justify-between" :class="ESTADO_STYLE[estado].header">
          <div class="flex items-center gap-2">
            <span class="h-2 w-2 rounded-full" :class="ESTADO_STYLE[estado].dot" />
            <span class="text-sm font-semibold text-foreground">{{ estado }}</span>
          </div>
          <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-white/70">
            {{ clientesByEstado(estado).length }}
          </span>
        </div>

        <!-- Tarjetas -->
        <div class="p-3 space-y-3 min-h-[120px] bg-slate-50/40">
          <div
            v-for="c in clientesByEstado(estado)"
            :key="c.id"
            class="bg-white rounded-lg border p-3.5 shadow-sm"
          >
            <!-- Nombre -->
            <div class="flex items-center gap-2 mb-2">
              <div class="h-7 w-7 flex-shrink-0 rounded-md bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
                {{ c.nombre_comercial?.slice(0, 2).toUpperCase() || '?' }}
              </div>
              <span class="text-sm font-semibold text-foreground leading-tight">{{ c.nombre_comercial }}</span>
            </div>

            <!-- Servicios -->
            <div class="flex flex-wrap gap-1 mb-3">
              <span
                v-for="s in (Array.isArray(c.servicios) ? c.servicios : [])"
                :key="s"
                class="px-2 py-0.5 text-xs rounded-full bg-primary/10 text-primary"
              >{{ s }}</span>
              <span v-if="!c.servicios?.length" class="text-xs text-muted-foreground">Sin servicios</span>
            </div>

            <!-- Drive link -->
            <a
              v-if="c.folder_url"
              :href="c.folder_url"
              target="_blank"
              class="text-xs text-primary hover:underline flex items-center gap-1 mb-3"
            >
              <ExternalLink class="h-3 w-3" /> Carpeta Drive
            </a>

            <!-- Mover a otro estado -->
            <div class="border-t pt-2.5 mt-1">
              <p class="text-xs text-muted-foreground mb-1.5">Mover a:</p>
              <div class="flex gap-1 flex-wrap">
                <button
                  v-for="e in ESTADOS.filter(s => s !== estado)"
                  :key="e"
                  :disabled="saving === c.id"
                  :class="[
                    'px-2 py-1 text-xs rounded-md border transition-colors',
                    saving === c.id
                      ? 'opacity-50 cursor-not-allowed'
                      : 'hover:bg-slate-100 border-slate-200 text-slate-600',
                  ]"
                  @click="changeEstado(c, e)"
                >
                  <Spinner v-if="saving === c.id" size="sm" class="inline mr-1" />
                  {{ e }}
                </button>
              </div>
            </div>
          </div>

          <!-- Columna vacía -->
          <div v-if="!clientesByEstado(estado).length" class="text-center py-6">
            <Briefcase class="h-6 w-6 mx-auto mb-2 text-slate-300" />
            <p class="text-xs text-muted-foreground">Sin deals</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
