<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/lib/api'
import Spinner from '@/components/ui/Spinner.vue'
import { AlertCircle, RefreshCw, Receipt, ChevronRight } from 'lucide-vue-next'

const loading = ref(false)
const error = ref('')
const liquidaciones = ref([])

const ETAPAS = [
  { id: 'RECOPILACION',       label: 'Recopilación',       color: 'text-muted-foreground', bg: 'bg-muted-foreground/10 border-muted-foreground/20' },
  { id: 'FACTURACION_ENERGIA', label: 'Facturación',        color: 'text-yellow-400',       bg: 'bg-yellow-400/10 border-yellow-400/20' },
  { id: 'CONTABILIZACION',    label: 'Contabilización',    color: 'text-blue-400',         bg: 'bg-blue-400/10 border-blue-400/20' },
  { id: 'MANDATOS',           label: 'Mandatos',           color: 'text-purple-400',       bg: 'bg-purple-400/10 border-purple-400/20' },
  { id: 'ENTREGADO',          label: 'Entregado',          color: 'text-green-400',        bg: 'bg-green-400/10 border-green-400/20' },
]

const porEtapa = computed(() => {
  return ETAPAS.map(etapa => ({
    ...etapa,
    items: liquidaciones.value.filter(l => l.estado === etapa.id),
  }))
})

const totales = computed(() => liquidaciones.value.reduce(
  (acc, l) => {
    acc.energia += Number(l.gen_total_kwh ?? 0)
    acc.ingresos += Number(l.ingreso_total_cop ?? 0)
    acc.margen += Number(l.margen_cop ?? 0)
    return acc
  },
  { energia: 0, ingresos: 0, margen: 0 }
))

function cop(val) {
  return Number(val ?? 0).toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
}

function kwh(val) {
  return Number(val ?? 0).toLocaleString('es-CO', { maximumFractionDigits: 0 }) + ' kWh'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/liquidaciones/', { params: { page_size: 200, ordering: '-periodo_inicio' } })
    liquidaciones.value = data.results ?? data
  } catch (e) {
    error.value = e.response?.status === 404
      ? 'Endpoint no disponible — asegúrate de correr el backend Django en :8000'
      : 'Error al cargar liquidaciones'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex flex-wrap items-center gap-3">
      <div class="flex items-center gap-2 flex-1">
        <Receipt class="h-5 w-5 text-primary" />
        <h1 class="text-2xl font-bold">Liquidaciones</h1>
      </div>
      <button
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border text-sm text-muted-foreground hover:text-foreground hover:border-primary transition-colors"
        @click="load"
      >
        <RefreshCw class="h-3.5 w-3.5" :class="{ 'animate-spin': loading }" />
        Actualizar
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <div class="rounded-xl border bg-card p-4">
        <div class="text-xs font-bold text-muted-foreground uppercase tracking-wide mb-1">Energía total</div>
        <div class="text-xl font-bold font-mono">{{ kwh(totales.energia) }}</div>
      </div>
      <div class="rounded-xl border bg-card p-4">
        <div class="text-xs font-bold text-muted-foreground uppercase tracking-wide mb-1">Ingresos totales</div>
        <div class="text-xl font-bold font-mono text-green-400">{{ cop(totales.ingresos) }}</div>
      </div>
      <div class="rounded-xl border bg-card p-4">
        <div class="text-xs font-bold text-muted-foreground uppercase tracking-wide mb-1">Margen neto</div>
        <div class="text-xl font-bold font-mono" :class="totales.margen >= 0 ? 'text-green-400' : 'text-red-400'">
          {{ cop(totales.margen) }}
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-if="error" class="rounded-xl border border-destructive/30 bg-destructive/10 p-6 text-center">
      <AlertCircle class="h-8 w-8 text-destructive mx-auto mb-2" />
      <p class="text-sm text-destructive font-medium">{{ error }}</p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="flex justify-center py-16">
      <Spinner size="lg" />
    </div>

    <!-- Pipeline Kanban -->
    <div v-else class="overflow-x-auto">
      <div class="flex gap-3 min-w-max pb-2">
        <div
          v-for="etapa in porEtapa"
          :key="etapa.id"
          class="w-72 flex-shrink-0"
        >
          <!-- Column header -->
          <div :class="['flex items-center gap-2 px-3 py-2 rounded-t-xl border-b-0 border rounded-b-none mb-0', etapa.bg]">
            <span :class="['text-xs font-bold uppercase tracking-wide', etapa.color]">{{ etapa.label }}</span>
            <span :class="['ml-auto text-xs font-mono font-bold px-1.5 py-0.5 rounded-full', etapa.bg, etapa.color]">
              {{ etapa.items.length }}
            </span>
          </div>

          <!-- Cards -->
          <div class="space-y-2 rounded-b-xl rounded-tr-xl bg-card border border-t-0 p-2 min-h-[120px]">
            <div
              v-for="liq in etapa.items"
              :key="liq.id"
              class="rounded-lg border border-border bg-background/40 p-3 hover:border-primary/40 transition-colors cursor-default"
            >
              <div class="flex items-start justify-between gap-2 mb-2">
                <div class="min-w-0">
                  <div class="text-sm font-semibold truncate">{{ liq.cliente_nombre ?? liq.cliente }}</div>
                  <div class="text-xs text-muted-foreground truncate">{{ liq.planta_nombre ?? liq.planta }}</div>
                </div>
              </div>
              <div class="text-xs text-muted-foreground font-mono">
                {{ liq.periodo_inicio }} → {{ liq.periodo_fin }}
              </div>
              <div class="mt-2 grid grid-cols-2 gap-1">
                <div class="text-xs">
                  <span class="text-muted-foreground">Energía</span>
                  <div class="font-mono font-semibold text-xs">{{ kwh(liq.gen_total_kwh) }}</div>
                </div>
                <div class="text-xs text-right">
                  <span class="text-muted-foreground">Ingreso</span>
                  <div class="font-mono font-semibold text-xs text-green-400">{{ cop(liq.ingreso_total_cop) }}</div>
                </div>
              </div>
            </div>

            <div v-if="!etapa.items.length" class="py-6 text-center">
              <p class="text-xs text-muted-foreground">Sin liquidaciones</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state global -->
    <div v-if="!loading && !error && !liquidaciones.length" class="rounded-xl border bg-card p-12 text-center">
      <Receipt class="h-10 w-10 text-muted-foreground mx-auto mb-3" />
      <p class="text-sm font-medium text-muted-foreground">No hay liquidaciones registradas</p>
      <p class="text-xs text-muted-foreground mt-1">Las liquidaciones aparecen aquí una vez creadas desde el backend</p>
    </div>
  </div>
</template>
