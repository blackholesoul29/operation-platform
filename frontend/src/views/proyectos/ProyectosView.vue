<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/lib/api'
import Spinner from '@/components/ui/Spinner.vue'
import { AlertCircle, RefreshCw, Zap, ChevronDown, ChevronUp } from 'lucide-vue-next'

const loading = ref(false)
const error = ref('')
const plantas = ref([])
const expandedId = ref(null)

const ESTADOS = {
  CONSTRUCCION:    { label: 'Construcción',    class: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/25' },
  PRUEBAS:         { label: 'Pruebas',         class: 'text-blue-400 bg-blue-400/10 border-blue-400/25' },
  OPERACION:       { label: 'Operación',       class: 'text-green-400 bg-green-400/10 border-green-400/25' },
  SUSPENDIDA:      { label: 'Suspendida',      class: 'text-red-400 bg-red-400/10 border-red-400/25' },
  BAJA:            { label: 'Baja',            class: 'text-muted-foreground bg-muted-foreground/10 border-muted-foreground/25' },
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/proyectos/plantas/', { params: { page_size: 200, ordering: 'nombre' } })
    plantas.value = data.results ?? data
  } catch (e) {
    error.value = e.response?.status === 404
      ? 'Endpoint no disponible — asegúrate de correr el backend Django en :8000'
      : 'Error al cargar plantas'
  } finally {
    loading.value = false
  }
}

function toggle(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function mwp(kw) {
  if (!kw) return '—'
  const v = Number(kw)
  return v >= 1000 ? (v / 1000).toFixed(2) + ' MWp' : v.toFixed(0) + ' kWp'
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex flex-wrap items-center gap-3">
      <div class="flex items-center gap-2 flex-1">
        <Zap class="h-5 w-5 text-primary" />
        <h1 class="text-2xl font-bold">Proyectos — Info Técnica</h1>
      </div>
      <button
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border text-sm text-muted-foreground hover:text-foreground hover:border-primary transition-colors"
        @click="load"
      >
        <RefreshCw class="h-3.5 w-3.5" :class="{ 'animate-spin': loading }" />
        Actualizar
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="rounded-xl border border-destructive/30 bg-destructive/10 p-6 text-center">
      <AlertCircle class="h-8 w-8 text-destructive mx-auto mb-2" />
      <p class="text-sm text-destructive font-medium">{{ error }}</p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="flex justify-center py-16">
      <Spinner size="lg" />
    </div>

    <!-- Plants list -->
    <div v-else-if="plantas.length" class="space-y-2">
      <div
        v-for="planta in plantas"
        :key="planta.id"
        class="rounded-xl border bg-card overflow-hidden"
      >
        <!-- Row header -->
        <button
          class="w-full flex items-center gap-4 px-5 py-4 text-left hover:bg-accent/10 transition-colors"
          @click="toggle(planta.id)"
        >
          <div class="flex-1 grid grid-cols-1 md:grid-cols-4 gap-2 md:gap-4 items-center">
            <div>
              <div class="text-sm font-bold">{{ planta.nombre }}</div>
              <div class="text-xs text-muted-foreground">{{ planta.municipio }}, {{ planta.departamento }}</div>
            </div>
            <div class="text-center">
              <span
                class="inline-block px-2 py-0.5 rounded-full text-xs font-bold border uppercase"
                :class="ESTADOS[planta.estado]?.class ?? 'text-muted-foreground bg-muted-foreground/10 border-muted-foreground/25'"
              >
                {{ ESTADOS[planta.estado]?.label ?? planta.estado }}
              </span>
            </div>
            <div class="text-center font-mono font-bold text-sm">{{ mwp(planta.potencia_instalada_kwp) }}</div>
            <div class="text-xs text-muted-foreground text-right">
              Op. desde: <span class="font-mono">{{ planta.fecha_inicio_operacion ?? '—' }}</span>
            </div>
          </div>
          <component :is="expandedId === planta.id ? ChevronUp : ChevronDown" class="h-4 w-4 text-muted-foreground flex-shrink-0" />
        </button>

        <!-- Expanded technical detail -->
        <div v-if="expandedId === planta.id" class="border-t border-border px-5 py-4 bg-background/30">
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-3 text-xs">
            <div>
              <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Código XM</div>
              <div class="font-mono">{{ planta.codigo_xm ?? '—' }}</div>
            </div>
            <div>
              <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Recurso</div>
              <div>{{ planta.recurso_generacion ?? '—' }}</div>
            </div>
            <div>
              <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Lat / Lon</div>
              <div class="font-mono">{{ planta.latitud ? `${planta.latitud}, ${planta.longitud}` : '—' }}</div>
            </div>
            <div>
              <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Inicio pruebas</div>
              <div class="font-mono">{{ planta.fecha_inicio_pruebas ?? '—' }}</div>
            </div>

            <!-- Frontera data if available -->
            <template v-if="planta.frontera">
              <div class="col-span-2 md:col-span-3 lg:col-span-4 border-t border-border pt-3 mt-1">
                <div class="text-muted-foreground font-bold uppercase tracking-wide mb-2">Frontera XM</div>
              </div>
              <div>
                <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Código Frontera</div>
                <div class="font-mono">{{ planta.frontera.codigo_frontera ?? '—' }}</div>
              </div>
              <div>
                <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Medidor Ppal.</div>
                <div class="font-mono">{{ planta.frontera.medidor_principal ?? '—' }}</div>
              </div>
              <div>
                <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Medidor Resp.</div>
                <div class="font-mono">{{ planta.frontera.medidor_respaldo ?? '—' }}</div>
              </div>
              <div>
                <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Operador Red</div>
                <div>{{ planta.frontera.operador_red ?? '—' }}</div>
              </div>
              <div>
                <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Nivel Tensión</div>
                <div>{{ planta.frontera.nivel_tension ?? '—' }}</div>
              </div>
              <div>
                <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">CT Relación</div>
                <div class="font-mono">{{ planta.frontera.ct_relacion_transformacion ?? '—' }}</div>
              </div>
              <div>
                <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">PT Relación</div>
                <div class="font-mono">{{ planta.frontera.pt_relacion_transformacion ?? '—' }}</div>
              </div>
              <div>
                <div class="text-muted-foreground font-bold uppercase tracking-wide mb-0.5">Factor Multiplicador</div>
                <div class="font-mono">{{ planta.frontera.factor_multiplicador ?? '—' }}</div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="rounded-xl border bg-card p-12 text-center">
      <Zap class="h-10 w-10 text-muted-foreground mx-auto mb-3" />
      <p class="text-sm font-medium text-muted-foreground">No hay plantas registradas</p>
      <p class="text-xs text-muted-foreground mt-1">Las plantas aparecen aquí una vez creadas desde el backend Django</p>
    </div>
  </div>
</template>
