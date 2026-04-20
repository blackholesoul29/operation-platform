<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/lib/api'
import Spinner from '@/components/ui/Spinner.vue'
import Badge from '@/components/ui/Badge.vue'
import {
  CheckCircle2, Clock, AlertCircle, ExternalLink, RefreshCw, Activity
} from 'lucide-vue-next'

const loading = ref(false)
const error = ref('')
const reportes = ref([])
const completitud = ref([])
const mesActual = ref('')

const ESTADOS = {
  PENDIENTE: { label: 'Pendiente', variant: 'warning', icon: Clock },
  SUBIDO:    { label: 'Subido',    variant: 'info',    icon: CheckCircle2 },
  VALIDADO:  { label: 'Validado',  variant: 'success', icon: CheckCircle2 },
}

const resumen = computed(() => ({
  total:    reportes.value.length,
  validado: reportes.value.filter(r => r.estado === 'VALIDADO').length,
  subido:   reportes.value.filter(r => r.estado === 'SUBIDO').length,
  pendiente: reportes.value.filter(r => r.estado === 'PENDIENTE').length,
}))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const hoy = new Date()
    mesActual.value = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}`

    const [rRes, cRes] = await Promise.all([
      api.get('/cgm/reportes/', { params: { page_size: 200, ordering: '-fecha' } }),
      api.get('/cgm/reportes/completitud/', { params: { anio: hoy.getFullYear(), mes: hoy.getMonth() + 1 } }).catch(() => ({ data: [] })),
    ])
    reportes.value  = rRes.data.results ?? rRes.data
    completitud.value = Array.isArray(cRes.data) ? cRes.data : []
  } catch (e) {
    error.value = e.response?.status === 404
      ? 'Endpoint no disponible — asegúrate de correr el backend Django en :8000'
      : 'Error al cargar reportes CGM'
  } finally {
    loading.value = false
  }
}

function completitudPlanta(plantaId) {
  return completitud.value.find(c => c.planta_id === plantaId)
}

function pctColor(pct) {
  if (pct >= 95) return 'text-green-400'
  if (pct >= 70) return 'text-yellow-400'
  return 'text-red-400'
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex flex-wrap items-center gap-3">
      <div class="flex items-center gap-2 flex-1">
        <Activity class="h-5 w-5 text-primary" />
        <h1 class="text-2xl font-bold">CGM — Reportes de Frontera</h1>
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
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div class="rounded-xl border bg-card p-4">
        <div class="text-xs font-bold text-muted-foreground uppercase tracking-wide mb-1">Total reportes</div>
        <div class="text-2xl font-bold font-mono">{{ resumen.total }}</div>
      </div>
      <div class="rounded-xl border bg-card p-4">
        <div class="text-xs font-bold text-muted-foreground uppercase tracking-wide mb-1">Validados</div>
        <div class="text-2xl font-bold font-mono text-green-400">{{ resumen.validado }}</div>
      </div>
      <div class="rounded-xl border bg-card p-4">
        <div class="text-xs font-bold text-muted-foreground uppercase tracking-wide mb-1">Subidos</div>
        <div class="text-2xl font-bold font-mono text-blue-400">{{ resumen.subido }}</div>
      </div>
      <div class="rounded-xl border bg-card p-4">
        <div class="text-xs font-bold text-muted-foreground uppercase tracking-wide mb-1">Pendientes</div>
        <div class="text-2xl font-bold font-mono text-yellow-400">{{ resumen.pendiente }}</div>
      </div>
    </div>

    <!-- Completitud por planta -->
    <div v-if="completitud.length" class="rounded-xl border bg-card">
      <div class="px-5 py-3 border-b border-border flex items-center gap-2">
        <span class="text-xs font-bold text-muted-foreground uppercase tracking-wide">Completitud {{ mesActual }}</span>
      </div>
      <div class="divide-y divide-border">
        <div
          v-for="c in completitud"
          :key="c.planta_id"
          class="flex items-center gap-4 px-5 py-3"
        >
          <div class="flex-1 min-w-0">
            <div class="text-sm font-semibold truncate">{{ c.planta_nombre }}</div>
            <div class="text-xs text-muted-foreground">{{ c.dias_subidos }}/{{ c.dias_mes }} días con reporte</div>
          </div>
          <div class="w-32">
            <div class="flex items-center justify-between mb-1">
              <span :class="['text-sm font-bold font-mono', pctColor(c.completitud_pct)]">{{ c.completitud_pct }}%</span>
            </div>
            <div class="h-1.5 rounded-full bg-border overflow-hidden">
              <div
                class="h-full rounded-full transition-all"
                :class="c.completitud_pct >= 95 ? 'bg-green-400' : c.completitud_pct >= 70 ? 'bg-yellow-400' : 'bg-red-400'"
                :style="{ width: c.completitud_pct + '%' }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-if="error" class="rounded-xl border border-destructive/30 bg-destructive/10 p-6 text-center">
      <AlertCircle class="h-8 w-8 text-destructive mx-auto mb-2" />
      <p class="text-sm text-destructive font-medium">{{ error }}</p>
    </div>

    <!-- Loading state -->
    <div v-else-if="loading" class="flex justify-center py-16">
      <Spinner size="lg" />
    </div>

    <!-- Reportes table -->
    <div v-else-if="reportes.length" class="rounded-xl border bg-card overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-border bg-background/40">
            <th class="text-left px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wide">Planta</th>
            <th class="text-left px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wide">Fecha</th>
            <th class="text-left px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wide">Estado</th>
            <th class="text-right px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wide">Generación (kWh)</th>
            <th class="text-center px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wide">Drive</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border">
          <tr
            v-for="r in reportes"
            :key="r.id"
            class="hover:bg-accent/10 transition-colors"
          >
            <td class="px-4 py-3 font-medium">{{ r.planta_nombre ?? r.planta }}</td>
            <td class="px-4 py-3 text-muted-foreground font-mono text-xs">{{ r.fecha }}</td>
            <td class="px-4 py-3">
              <span
                class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold uppercase"
                :class="{
                  'bg-yellow-400/10 text-yellow-400 border border-yellow-400/25': r.estado === 'PENDIENTE',
                  'bg-blue-400/10 text-blue-400 border border-blue-400/25': r.estado === 'SUBIDO',
                  'bg-green-400/10 text-green-400 border border-green-400/25': r.estado === 'VALIDADO',
                }"
              >
                {{ ESTADOS[r.estado]?.label ?? r.estado }}
              </span>
            </td>
            <td class="px-4 py-3 text-right font-mono">
              {{ r.balance?.gen_total != null ? Number(r.balance.gen_total).toLocaleString('es-CO') : '—' }}
            </td>
            <td class="px-4 py-3 text-center">
              <a
                v-if="r.google_drive_url"
                :href="r.google_drive_url"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex text-primary hover:text-primary/70 transition-colors"
                title="Abrir en Drive"
              >
                <ExternalLink class="h-4 w-4" />
              </a>
              <span v-else class="text-muted-foreground">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading && !error" class="rounded-xl border bg-card p-12 text-center">
      <Activity class="h-10 w-10 text-muted-foreground mx-auto mb-3" />
      <p class="text-sm font-medium text-muted-foreground">No hay reportes registrados</p>
      <p class="text-xs text-muted-foreground mt-1">Los reportes CGM aparecen aquí una vez cargados desde el backend</p>
    </div>
  </div>
</template>
