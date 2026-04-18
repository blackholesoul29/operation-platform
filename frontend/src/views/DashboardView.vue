<script setup>
import { onMounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import {
  TrendingUp,
  CheckCircle,
  DollarSign,
  Target,
  ArrowRight,
  CheckSquare,
  Bell,
} from 'lucide-vue-next'
import { useDashboardStore } from '@/stores/dashboard'
import { useTareasStore } from '@/stores/tareas'
import { useNotificacionesStore } from '@/stores/notificaciones'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EtapaBadge from '@/components/common/EtapaBadge.vue'
import { formatCurrency, formatRelativeDate, ETAPAS_CONFIG, isOverdue } from '@/lib/utils'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

const dashStore = useDashboardStore()
const tareasStore = useTareasStore()
const notifStore = useNotificacionesStore()
const router = useRouter()

onMounted(async () => {
  await Promise.all([
    dashStore.fetchStats(),
    tareasStore.fetchTareas({ completada: false, limit: 5 }),
    notifStore.fetchNotificaciones({ limit: 5 }),
  ])
})

const kpis = computed(() => [
  {
    label: 'Deals Activos',
    value: dashStore.stats.deals_activos ?? 0,
    icon: TrendingUp,
    color: 'bg-blue-50 text-blue-600',
    border: 'border-blue-100',
  },
  {
    label: 'Cerrados este Mes',
    value: dashStore.stats.deals_cerrados_mes ?? 0,
    icon: CheckCircle,
    color: 'bg-green-50 text-green-600',
    border: 'border-green-100',
  },
  {
    label: 'Valor Pipeline',
    value: formatCurrency(dashStore.stats.valor_pipeline_total ?? 0),
    icon: DollarSign,
    color: 'bg-purple-50 text-purple-600',
    border: 'border-purple-100',
    isString: true,
  },
  {
    label: 'Tasa de Conversión',
    value: `${(dashStore.stats.tasa_conversion ?? 0).toFixed(1)}%`,
    icon: Target,
    color: 'bg-orange-50 text-orange-600',
    border: 'border-orange-100',
    isString: true,
  },
])

// Bar chart data
const barChartData = computed(() => {
  const etapas = ['prospeccion', 'primer_contacto', 'oferta_enviada', 'negociacion', 'contrato']
  const data = dashStore.stats.deals_por_etapa || {}
  return {
    labels: etapas.map((e) => ETAPAS_CONFIG[e]?.label || e),
    datasets: [
      {
        label: 'Deals',
        data: etapas.map((e) => data[e] || 0),
        backgroundColor: [
          'rgba(100,116,139,0.7)',
          'rgba(59,130,246,0.7)',
          'rgba(234,179,8,0.7)',
          'rgba(249,115,22,0.7)',
          'rgba(168,85,247,0.7)',
        ],
        borderRadius: 6,
        borderSkipped: false,
      },
    ],
  }
})

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => ` ${ctx.parsed.y} deals` } },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { stepSize: 1 },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
    x: { grid: { display: false } },
  },
}

// Doughnut chart
const doughnutData = computed(() => {
  const data = dashStore.stats.deals_por_servicio || {}
  const labels = Object.keys(data)
  const values = Object.values(data)
  const colors = ['#6366f1','#0ea5e9','#22c55e','#f97316','#a855f7','#ec4899']
  return {
    labels: labels.map((l) => {
      const map = {
        representacion: 'Representación',
        cgm: 'CGM',
        monitoreo: 'Monitoreo',
        ppa: 'PPA',
        venta_energia: 'Venta Energía',
        recs: 'RECs',
      }
      return map[l] || l
    }),
    datasets: [{
      data: values,
      backgroundColor: colors.slice(0, labels.length),
      borderWidth: 2,
      borderColor: '#ffffff',
      hoverOffset: 4,
    }],
  }
})

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { padding: 16, font: { size: 12 } } },
  },
}

const tareasPendientes = computed(() =>
  tareasStore.tareas.filter((t) => !t.completada).slice(0, 5)
)

const notificacionesRecientes = computed(() =>
  notifStore.notificaciones.slice(0, 5)
)
</script>

<template>
  <div class="space-y-6">
    <!-- KPI Row -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <Card
        v-for="kpi in kpis"
        :key="kpi.label"
        :class="['border', kpi.border]"
      >
        <CardContent class="p-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted-foreground font-medium">{{ kpi.label }}</p>
              <p class="text-2xl font-bold text-foreground mt-1">
                <span v-if="dashStore.loading" class="inline-block h-6 w-20 bg-muted animate-pulse rounded" />
                <span v-else>{{ kpi.value }}</span>
              </p>
            </div>
            <div :class="['flex h-12 w-12 items-center justify-center rounded-xl', kpi.color]">
              <component :is="kpi.icon" class="h-6 w-6" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Bar chart -->
      <Card>
        <CardHeader class="pb-3">
          <CardTitle class="text-base">Deals por Etapa</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="h-64">
            <div v-if="dashStore.loading" class="flex h-full items-center justify-center">
              <Spinner size="lg" />
            </div>
            <Bar v-else :data="barChartData" :options="barChartOptions" />
          </div>
        </CardContent>
      </Card>

      <!-- Doughnut chart -->
      <Card>
        <CardHeader class="pb-3">
          <CardTitle class="text-base">Deals por Tipo de Servicio</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="h-64">
            <div v-if="dashStore.loading" class="flex h-full items-center justify-center">
              <Spinner size="lg" />
            </div>
            <div
              v-else-if="!doughnutData.datasets[0].data.length || doughnutData.datasets[0].data.every(v => !v)"
              class="flex h-full flex-col items-center justify-center text-muted-foreground"
            >
              <p class="text-sm">Sin datos disponibles</p>
            </div>
            <Doughnut v-else :data="doughnutData" :options="doughnutOptions" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Bottom Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Tasks -->
      <Card>
        <CardHeader class="pb-3">
          <div class="flex items-center justify-between">
            <CardTitle class="text-base flex items-center gap-2">
              <CheckSquare class="h-4 w-4 text-primary" />
              Mis Tareas Pendientes
            </CardTitle>
            <button
              class="text-xs text-primary hover:underline flex items-center gap-1"
              @click="router.push('/tareas')"
            >
              Ver todas <ArrowRight class="h-3 w-3" />
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <div v-if="tareasStore.loading" class="flex justify-center py-6">
            <Spinner />
          </div>
          <div v-else-if="!tareasPendientes.length" class="text-center py-8 text-sm text-muted-foreground">
            No tienes tareas pendientes
          </div>
          <ul v-else class="space-y-2">
            <li
              v-for="tarea in tareasPendientes"
              :key="tarea.id"
              class="flex items-start gap-2.5 rounded-lg p-2 hover:bg-muted/40 transition-colors cursor-pointer"
              @click="router.push('/tareas')"
            >
              <span
                :class="[
                  'mt-0.5 h-2 w-2 flex-shrink-0 rounded-full',
                  tarea.prioridad === 'urgente' ? 'bg-red-500' :
                  tarea.prioridad === 'alta' ? 'bg-orange-500' :
                  tarea.prioridad === 'media' ? 'bg-yellow-400' : 'bg-gray-300'
                ]"
              />
              <div class="min-w-0">
                <p class="text-sm font-medium text-foreground truncate">{{ tarea.titulo }}</p>
                <p
                  v-if="tarea.fecha_limite"
                  :class="['text-xs mt-0.5', isOverdue(tarea.fecha_limite) ? 'text-destructive font-medium' : 'text-muted-foreground']"
                >
                  {{ isOverdue(tarea.fecha_limite) ? 'Vencida: ' : 'Vence: ' }}{{ tarea.fecha_limite }}
                </p>
              </div>
            </li>
          </ul>
        </CardContent>
      </Card>

      <!-- Notifications -->
      <Card>
        <CardHeader class="pb-3">
          <div class="flex items-center justify-between">
            <CardTitle class="text-base flex items-center gap-2">
              <Bell class="h-4 w-4 text-primary" />
              Notificaciones Recientes
            </CardTitle>
            <button
              class="text-xs text-primary hover:underline flex items-center gap-1"
              @click="router.push('/notificaciones')"
            >
              Ver todas <ArrowRight class="h-3 w-3" />
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <div v-if="notifStore.loading" class="flex justify-center py-6">
            <Spinner />
          </div>
          <div v-else-if="!notificacionesRecientes.length" class="text-center py-8 text-sm text-muted-foreground">
            No tienes notificaciones recientes
          </div>
          <ul v-else class="space-y-2">
            <li
              v-for="notif in notificacionesRecientes"
              :key="notif.id"
              :class="[
                'rounded-lg p-2.5 cursor-pointer transition-colors',
                !notif.leida ? 'bg-blue-50 hover:bg-blue-100/70' : 'hover:bg-muted/40',
              ]"
              @click="router.push('/notificaciones')"
            >
              <div class="flex items-start gap-2">
                <span
                  v-if="!notif.leida"
                  class="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-primary"
                />
                <div class="min-w-0">
                  <p class="text-sm font-medium text-foreground leading-snug">{{ notif.titulo || notif.mensaje }}</p>
                  <p v-if="notif.titulo" class="text-xs text-muted-foreground mt-0.5 line-clamp-1">{{ notif.mensaje }}</p>
                  <p class="text-xs text-muted-foreground mt-0.5">{{ formatRelativeDate(notif.created_at) }}</p>
                </div>
              </div>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
