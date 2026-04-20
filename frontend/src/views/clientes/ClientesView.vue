<script setup>
import { ref, computed, onMounted } from 'vue'
import { useClientesStore } from '@/stores/clientes'
import { Search, ExternalLink, FolderOpen } from 'lucide-vue-next'
import Input from '@/components/ui/Input.vue'
import Spinner from '@/components/ui/Spinner.vue'

const store = useClientesStore()
const search = ref('')
const servicioFilter = ref('')

const SERVICIOS = ['CGM', 'Representación', 'Operación', 'PPA']

const SERVICIO_OPTIONS = [
  { value: '', label: 'Todos los servicios' },
  ...SERVICIOS.map(s => ({ value: s, label: s })),
]

const DOCS = [
  { key: 'razon_social', label: 'Razón Social' },
  { key: 'nit', label: 'NIT' },
  { key: 'rut', label: 'RUT' },
  { key: 'camara_comercio', label: 'Cámara de Comercio' },
  { key: 'nda', label: 'NDA' },
  { key: 'oferta', label: 'Oferta' },
  { key: 'cert_bancaria', label: 'Cert. Bancaria' },
]

onMounted(() => store.fetchClientes())

const filteredClientes = computed(() => {
  let list = store.clientes
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(c => c.nombre_comercial?.toLowerCase().includes(q))
  }
  if (servicioFilter.value) {
    list = list.filter(c =>
      Array.isArray(c.servicios) && c.servicios.includes(servicioFilter.value)
    )
  }
  return list
})

const estadoClass = (e) => ({
  Originación: 'bg-amber-100 text-amber-800',
  Negociación: 'bg-blue-100 text-blue-800',
  Cierre: 'bg-green-100 text-green-800',
}[e] || 'bg-slate-100 text-slate-700')
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <h1 class="text-2xl font-bold flex-1">Listado de Clientes y Servicios</h1>
      <span class="text-sm text-muted-foreground">{{ filteredClientes.length }} cliente(s)</span>
    </div>

    <!-- Filtros -->
    <div class="flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-[200px] max-w-xs">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input v-model="search" placeholder="Buscar por nombre..." class="pl-9" />
      </div>
      <div class="flex gap-1 bg-slate-100 rounded-lg p-1">
        <button
          v-for="opt in SERVICIO_OPTIONS"
          :key="opt.value"
          :class="[
            'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
            servicioFilter === opt.value
              ? 'bg-white text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground',
          ]"
          @click="servicioFilter = opt.value"
        >{{ opt.label }}</button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16"><Spinner size="lg" /></div>

    <!-- Error -->
    <div v-else-if="store.error" class="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
      {{ store.error }}
    </div>

    <!-- Vacío -->
    <div v-else-if="!filteredClientes.length" class="text-center py-16 text-muted-foreground">
      <FolderOpen class="h-10 w-10 mx-auto mb-3 opacity-30" />
      <p class="text-sm">No hay clientes que coincidan con los filtros.</p>
    </div>

    <!-- Tarjetas de clientes -->
    <div v-else class="grid gap-4">
      <div
        v-for="c in filteredClientes"
        :key="c.id"
        class="rounded-xl border bg-card shadow-sm p-5"
      >
        <!-- Cabecera de la tarjeta -->
        <div class="flex items-start justify-between gap-4 mb-4">
          <div class="flex items-center gap-3">
            <div class="h-10 w-10 flex-shrink-0 rounded-lg bg-primary/10 flex items-center justify-center text-sm font-bold text-primary">
              {{ c.nombre_comercial?.slice(0, 2).toUpperCase() || '?' }}
            </div>
            <div>
              <h2 class="font-semibold text-foreground">{{ c.nombre_comercial }}</h2>
              <a
                v-if="c.folder_url"
                :href="c.folder_url"
                target="_blank"
                class="text-xs text-primary hover:underline flex items-center gap-1 mt-0.5"
              >
                <ExternalLink class="h-3 w-3" /> Carpeta Drive
              </a>
            </div>
          </div>
          <span :class="['px-2.5 py-1 text-xs font-semibold rounded-full flex-shrink-0', estadoClass(c.estado)]">
            {{ c.estado || '—' }}
          </span>
        </div>

        <!-- Servicios -->
        <div class="mb-4">
          <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Servicios contratados</p>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="s in (Array.isArray(c.servicios) ? c.servicios : [])"
              :key="s"
              class="px-2.5 py-1 text-xs font-medium rounded-full bg-primary/10 text-primary"
            >{{ s }}</span>
            <span v-if="!c.servicios?.length" class="text-xs text-muted-foreground">Sin servicios asignados</span>
          </div>
        </div>

        <!-- Documentos -->
        <div>
          <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Documentos</p>
          <div class="flex flex-wrap gap-2">
            <a
              v-for="doc in DOCS.filter(d => c[`${d.key}_url`])"
              :key="doc.key"
              :href="c[`${doc.key}_url`]"
              target="_blank"
              class="flex items-center gap-1 px-2.5 py-1 text-xs rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
            >
              <ExternalLink class="h-3 w-3" />
              {{ doc.label }}
            </a>
            <span
              v-for="doc in DOCS.filter(d => !c[`${d.key}_url`])"
              :key="`missing-${doc.key}`"
              class="px-2.5 py-1 text-xs rounded-lg bg-slate-50 text-slate-400 border border-dashed border-slate-200"
            >
              {{ doc.label }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
