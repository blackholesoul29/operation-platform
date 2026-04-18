<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDealsStore } from '@/stores/deals'
import {
  ArrowLeft, Edit, ChevronDown, Phone, Users, Mail, FileText, ArrowRight,
  Paperclip, CheckSquare, CheckCircle, AlertCircle, XCircle, Plus, Send,
} from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Badge from '@/components/ui/Badge.vue'
import Spinner from '@/components/ui/Spinner.vue'
import Separator from '@/components/ui/Separator.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Select from '@/components/ui/Select.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import Avatar from '@/components/ui/Avatar.vue'
import EtapaBadge from '@/components/common/EtapaBadge.vue'
import ServicioBadge from '@/components/common/ServicioBadge.vue'
import DocumentUpload from '@/components/documentos/DocumentUpload.vue'
import {
  formatCurrency, formatDate, formatRelativeDate,
  ETAPAS_CONFIG, ETAPAS_ORDER, TIPO_ACTIVIDAD_CONFIG, getInitials
} from '@/lib/utils'

const route = useRoute()
const router = useRouter()
const dealsStore = useDealsStore()

const deal = computed(() => dealsStore.currentDeal)
const loading = ref(true)
const changingEtapa = ref(false)
const changeEtapaModal = ref(false)
const pendingEtapa = ref('')
const motivoEtapa = ref('')
const addingActivity = ref(false)
const activityForm = ref({ tipo: 'nota', descripcion: '' })
const activityLoading = ref(false)
const uploadDocModal = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    await dealsStore.fetchDeal(route.params.id)
  } finally {
    loading.value = false
  }
})

const ETAPAS_ACTIVAS = ['prospeccion', 'primer_contacto', 'oferta_enviada', 'negociacion', 'contrato']

const progressPercent = computed(() => {
  if (!deal.value) return 0
  const idx = ETAPAS_ACTIVAS.indexOf(deal.value.etapa)
  if (idx === -1) return 100
  return Math.round(((idx + 1) / ETAPAS_ACTIVAS.length) * 100)
})

const etapaMenuItems = computed(() =>
  Object.entries(ETAPAS_CONFIG).map(([key, cfg]) => ({
    label: cfg.label,
    action: () => {
      pendingEtapa.value = key
      motivoEtapa.value = ''
      changeEtapaModal.value = true
    },
  }))
)

async function confirmEtapaChange() {
  changingEtapa.value = true
  try {
    await dealsStore.cambiarEtapa(deal.value.id, {
      etapa: pendingEtapa.value,
      motivo: motivoEtapa.value,
    })
    changeEtapaModal.value = false
  } finally {
    changingEtapa.value = false
  }
}

async function submitActivity() {
  if (!activityForm.value.descripcion.trim()) return
  activityLoading.value = true
  try {
    await dealsStore.addActividad(deal.value.id, activityForm.value)
    activityForm.value = { tipo: 'nota', descripcion: '' }
    addingActivity.value = false
  } finally {
    activityLoading.value = false
  }
}

const ACTIVIDAD_TIPO_OPTIONS = [
  { value: 'nota', label: 'Nota' },
  { value: 'llamada', label: 'Llamada' },
  { value: 'reunion', label: 'Reunión' },
  { value: 'email', label: 'Email' },
]

function actividadIcon(tipo) {
  const icons = { llamada: Phone, reunion: Users, email: Mail, nota: FileText, cambio_etapa: ArrowRight, documento: Paperclip, tarea: CheckSquare }
  return icons[tipo] || FileText
}

function actividadColor(tipo) {
  const cfg = TIPO_ACTIVIDAD_CONFIG[tipo]
  return cfg?.color || 'text-gray-500 bg-gray-50'
}

function docStatusIcon(estado) {
  if (estado === 'aprobado') return CheckCircle
  if (estado === 'pendiente') return AlertCircle
  return XCircle
}

function docStatusColor(estado) {
  if (estado === 'aprobado') return 'text-green-500'
  if (estado === 'pendiente') return 'text-amber-500'
  return 'text-red-500'
}
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-20">
      <Spinner size="xl" />
    </div>

    <div v-else-if="!deal" class="text-center py-20 text-muted-foreground">
      Deal no encontrado.
      <Button variant="link" @click="router.push('/deals')">Volver a deals</Button>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="flex flex-wrap items-center gap-3 mb-6">
        <button
          class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
          @click="router.push('/deals')"
        >
          <ArrowLeft class="h-4 w-4" />
          Deals
        </button>
        <Separator orientation="vertical" class="h-4" />
        <h1 class="text-xl font-bold text-foreground flex-1 min-w-0 truncate">{{ deal.nombre }}</h1>
        <EtapaBadge :etapa="deal.etapa" />
        <div class="flex items-center gap-2 flex-shrink-0">
          <DropdownMenu :items="etapaMenuItems" align="right">
            <template #trigger>
              <Button variant="outline" size="sm">
                Cambiar etapa
                <ChevronDown class="h-3.5 w-3.5 ml-1" />
              </Button>
            </template>
          </DropdownMenu>
          <Button size="sm" @click="router.push(`/deals/${deal.id}/editar`)">
            <Edit class="h-3.5 w-3.5 mr-1" />
            Editar
          </Button>
        </div>
      </div>

      <!-- Stage progress bar -->
      <div class="mb-6">
        <div class="flex justify-between mb-1.5">
          <span
            v-for="etapa in ETAPAS_ACTIVAS"
            :key="etapa"
            :class="[
              'text-xs font-medium',
              deal.etapa === etapa ? 'text-primary' : 'text-muted-foreground',
            ]"
          >
            {{ ETAPAS_CONFIG[etapa]?.label }}
          </span>
        </div>
        <div class="h-2 w-full rounded-full bg-muted overflow-hidden">
          <div
            class="h-full rounded-full bg-primary transition-all duration-500"
            :style="{ width: `${progressPercent}%` }"
          />
        </div>
      </div>

      <!-- 3-column layout -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">

        <!-- LEFT: Info -->
        <div class="lg:col-span-3 space-y-4">
          <!-- Basic info -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-sm">Información del Deal</CardTitle>
            </CardHeader>
            <CardContent class="space-y-3">
              <div>
                <p class="text-xs text-muted-foreground">Cliente</p>
                <p class="text-sm font-medium cursor-pointer text-primary hover:underline" @click="router.push(`/clientes/${deal.cliente?.id}`)">
                  {{ deal.cliente?.nombre || '—' }}
                </p>
              </div>
              <div>
                <p class="text-xs text-muted-foreground">NIT</p>
                <p class="text-sm">{{ deal.cliente?.nit || '—' }}</p>
              </div>
              <div>
                <p class="text-xs text-muted-foreground">Tipo Pipeline</p>
                <p class="text-sm font-medium">{{ deal.tipo_pipeline === 'recs' ? 'RECs' : 'Servicios Principales' }}</p>
              </div>
              <div>
                <p class="text-xs text-muted-foreground">Origen</p>
                <p class="text-sm">{{ deal.origen || '—' }}</p>
              </div>
              <Separator />
              <div>
                <p class="text-xs text-muted-foreground">Comercial Asignado</p>
                <div class="flex items-center gap-2 mt-1">
                  <Avatar
                    :fallback="getInitials(`${deal.comercial_asignado?.first_name || ''} ${deal.comercial_asignado?.last_name || ''}`)"
                    size="sm"
                  />
                  <p class="text-sm font-medium">
                    {{ deal.comercial_asignado?.first_name || deal.comercial_asignado?.username || '—' }}
                  </p>
                </div>
              </div>
              <Separator />
              <div>
                <p class="text-xs text-muted-foreground">Valor Estimado</p>
                <p class="text-base font-bold text-foreground">{{ formatCurrency(deal.valor_estimado) }}</p>
              </div>
              <div>
                <p class="text-xs text-muted-foreground">Fecha Estimada Cierre</p>
                <p class="text-sm">{{ formatDate(deal.fecha_estimada_cierre) }}</p>
              </div>
              <div>
                <p class="text-xs text-muted-foreground mb-1">Probabilidad</p>
                <div class="flex items-center gap-2">
                  <div class="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                    <div
                      class="h-full rounded-full bg-primary transition-all"
                      :style="{ width: `${deal.probabilidad || 0}%` }"
                    />
                  </div>
                  <span class="text-xs font-semibold text-foreground">{{ deal.probabilidad || 0 }}%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Services -->
          <Card v-if="deal.servicios?.length">
            <CardHeader class="pb-3">
              <CardTitle class="text-sm">Servicios</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="flex flex-wrap gap-1.5">
                <ServicioBadge v-for="svc in deal.servicios" :key="svc" :servicio="svc" />
              </div>
            </CardContent>
          </Card>

          <!-- Technical info -->
          <Card v-if="deal.info_tecnica">
            <CardHeader class="pb-3">
              <CardTitle class="text-sm">Información Técnica</CardTitle>
            </CardHeader>
            <CardContent class="space-y-2">
              <div v-if="deal.info_tecnica.nombre_proyecto">
                <p class="text-xs text-muted-foreground">Proyecto</p>
                <p class="text-sm">{{ deal.info_tecnica.nombre_proyecto }}</p>
              </div>
              <div v-if="deal.info_tecnica.tecnologia">
                <p class="text-xs text-muted-foreground">Tecnología</p>
                <p class="text-sm">{{ deal.info_tecnica.tecnologia }}</p>
              </div>
              <div v-if="deal.info_tecnica.capacidad_kwp">
                <p class="text-xs text-muted-foreground">Capacidad</p>
                <p class="text-sm">{{ deal.info_tecnica.capacidad_kwp }} kWp</p>
              </div>
              <div v-if="deal.info_tecnica.generacion_mwh">
                <p class="text-xs text-muted-foreground">Generación estimada</p>
                <p class="text-sm">{{ deal.info_tecnica.generacion_mwh }} MWh/año</p>
              </div>
              <div v-if="deal.info_tecnica.latitud">
                <p class="text-xs text-muted-foreground">Coordenadas</p>
                <p class="text-sm">{{ deal.info_tecnica.latitud }}, {{ deal.info_tecnica.longitud }}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- CENTER: Activity timeline -->
        <div class="lg:col-span-5 space-y-4">
          <Card>
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-sm">Actividad</CardTitle>
                <Button size="sm" variant="outline" @click="addingActivity = !addingActivity">
                  <Plus class="h-3.5 w-3.5 mr-1" />
                  Agregar
                </Button>
              </div>
            </CardHeader>
            <CardContent class="space-y-4">
              <!-- Add activity form -->
              <Transition
                enter-active-class="transition duration-200"
                enter-from-class="opacity-0 -translate-y-2"
                enter-to-class="opacity-100 translate-y-0"
              >
                <div v-if="addingActivity" class="rounded-lg border bg-muted/30 p-4 space-y-3">
                  <Select
                    v-model="activityForm.tipo"
                    :options="ACTIVIDAD_TIPO_OPTIONS"
                    class="w-full"
                  />
                  <Textarea
                    v-model="activityForm.descripcion"
                    placeholder="Escribe los detalles de la actividad..."
                    class="min-h-[80px]"
                  />
                  <div class="flex gap-2">
                    <Button size="sm" variant="outline" @click="addingActivity = false">Cancelar</Button>
                    <Button size="sm" :disabled="activityLoading || !activityForm.descripcion.trim()" @click="submitActivity">
                      <Spinner v-if="activityLoading" size="sm" class="mr-1" />
                      <Send class="h-3.5 w-3.5 mr-1" />
                      Guardar
                    </Button>
                  </div>
                </div>
              </Transition>

              <!-- Timeline -->
              <div v-if="!deal.actividades?.length" class="text-center py-8 text-sm text-muted-foreground">
                Sin actividad registrada
              </div>
              <div v-else class="relative">
                <div class="absolute left-4 top-4 bottom-4 w-0.5 bg-border" />
                <ul class="space-y-4">
                  <li
                    v-for="act in deal.actividades"
                    :key="act.id"
                    class="relative pl-10"
                  >
                    <div
                      :class="['absolute left-0 flex h-8 w-8 items-center justify-center rounded-full border-2 border-background', actividadColor(act.tipo)]"
                    >
                      <component :is="actividadIcon(act.tipo)" class="h-4 w-4" />
                    </div>
                    <div class="rounded-lg border bg-background p-3 shadow-sm">
                      <div class="flex items-center justify-between mb-1">
                        <span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                          {{ TIPO_ACTIVIDAD_CONFIG[act.tipo]?.label || act.tipo }}
                        </span>
                        <span class="text-xs text-muted-foreground">{{ formatRelativeDate(act.created_at) }}</span>
                      </div>
                      <p class="text-sm text-foreground whitespace-pre-wrap">{{ act.descripcion }}</p>
                      <p v-if="act.usuario" class="text-xs text-muted-foreground mt-2">
                        — {{ act.usuario?.first_name || act.usuario?.username }}
                      </p>
                    </div>
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- RIGHT: Docs & Tasks -->
        <div class="lg:col-span-4 space-y-4">
          <!-- Documents -->
          <Card>
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-sm">Documentos</CardTitle>
                <Button size="sm" variant="outline" @click="uploadDocModal = true">
                  <Plus class="h-3.5 w-3.5 mr-1" />
                  Subir
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div v-if="!deal.documentos?.length" class="text-center py-6 text-sm text-muted-foreground">
                Sin documentos
              </div>
              <ul v-else class="space-y-2">
                <li
                  v-for="doc in deal.documentos"
                  :key="doc.id"
                  class="flex items-center gap-2.5 rounded-md p-2 hover:bg-muted/40 transition-colors"
                >
                  <component
                    :is="docStatusIcon(doc.estado)"
                    :class="['h-4 w-4 flex-shrink-0', docStatusColor(doc.estado)]"
                  />
                  <div class="min-w-0 flex-1">
                    <p class="text-sm font-medium truncate">{{ doc.nombre }}</p>
                    <p class="text-xs text-muted-foreground">{{ doc.tipo_documento_display || doc.tipo_documento }}</p>
                  </div>
                  <a
                    v-if="doc.archivo"
                    :href="doc.archivo"
                    target="_blank"
                    class="text-xs text-primary hover:underline flex-shrink-0"
                    @click.stop
                  >
                    Ver
                  </a>
                </li>
              </ul>
            </CardContent>
          </Card>

          <!-- Tasks -->
          <Card>
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-sm">Tareas</CardTitle>
                <Button size="sm" variant="outline" @click="router.push('/tareas')">
                  <Plus class="h-3.5 w-3.5 mr-1" />
                  Nueva
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div v-if="!deal.tareas?.length" class="text-center py-6 text-sm text-muted-foreground">
                Sin tareas
              </div>
              <ul v-else class="space-y-2">
                <li
                  v-for="tarea in deal.tareas"
                  :key="tarea.id"
                  class="flex items-center gap-2 rounded-md p-2 hover:bg-muted/40 transition-colors"
                >
                  <div
                    :class="[
                      'h-4 w-4 flex-shrink-0 rounded-full border-2 flex items-center justify-center',
                      tarea.completada ? 'border-green-500 bg-green-500' : 'border-border',
                    ]"
                  >
                    <svg v-if="tarea.completada" class="h-2.5 w-2.5 text-white" viewBox="0 0 12 12" fill="none">
                      <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                  <div class="min-w-0 flex-1">
                    <p :class="['text-sm truncate', tarea.completada ? 'line-through text-muted-foreground' : '']">
                      {{ tarea.titulo }}
                    </p>
                    <p v-if="tarea.fecha_limite" class="text-xs text-muted-foreground">
                      {{ formatDate(tarea.fecha_limite) }}
                    </p>
                  </div>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </template>

    <!-- Change etapa modal -->
    <Dialog :open="changeEtapaModal" size="sm" @update:open="changeEtapaModal = $event">
      <DialogHeader>
        <DialogTitle>Cambiar Etapa</DialogTitle>
      </DialogHeader>
      <div class="px-6 pb-4 space-y-3">
        <div class="flex items-center gap-2">
          <EtapaBadge :etapa="deal?.etapa" />
          <ArrowRight class="h-4 w-4 text-muted-foreground" />
          <EtapaBadge :etapa="pendingEtapa" />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">Motivo (opcional)</label>
          <Textarea v-model="motivoEtapa" placeholder="Motivo del cambio..." />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="changeEtapaModal = false">Cancelar</Button>
        <Button :disabled="changingEtapa" @click="confirmEtapaChange">
          <Spinner v-if="changingEtapa" size="sm" class="mr-2" />
          Confirmar
        </Button>
      </DialogFooter>
    </Dialog>

    <!-- Upload document modal -->
    <Dialog :open="uploadDocModal" size="md" @update:open="uploadDocModal = $event">
      <DialogHeader>
        <DialogTitle>Subir Documento</DialogTitle>
      </DialogHeader>
      <div class="px-6 pb-6">
        <DocumentUpload
          :deal-id="deal?.id"
          :cliente-id="deal?.cliente?.id"
          @uploaded="uploadDocModal = false; dealsStore.fetchDeal(route.params.id)"
          @cancel="uploadDocModal = false"
        />
      </div>
    </Dialog>
  </div>
</template>
