<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDealsStore } from '@/stores/deals'
import { useClientesStore } from '@/stores/clientes'
import api from '@/lib/api'
import { ArrowLeft, Save } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Select from '@/components/ui/Select.vue'
import Separator from '@/components/ui/Separator.vue'
import Spinner from '@/components/ui/Spinner.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'

const route = useRoute()
const router = useRouter()
const dealsStore = useDealsStore()
const clientesStore = useClientesStore()

const isEdit = computed(() => !!route.params.id && route.name === 'deal-edit')
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const users = ref([])

const form = reactive({
  nombre: '',
  cliente: '',
  tipo_pipeline: 'servicios_principales',
  origen: '',
  servicios: [],
  comercial_asignado: '',
  valor_estimado: '',
  fecha_estimada_cierre: '',
  probabilidad: 50,
  // Technical
  nombre_proyecto: '',
  tecnologia: '',
  capacidad_kwp: '',
  generacion_mwh: '',
  latitud: '',
  longitud: '',
  operador_red: '',
  // RECs
  volumen_recs: '',
  periodo_redencion: '',
  registro_irec: '',
})

const SERVICIOS_OPTIONS = [
  { value: 'representacion', label: 'Representación' },
  { value: 'cgm', label: 'CGM' },
  { value: 'monitoreo', label: 'Monitoreo' },
  { value: 'ppa', label: 'PPA' },
  { value: 'venta_energia', label: 'Venta Energía' },
  { value: 'recs', label: 'RECs' },
]

const ORIGEN_OPTIONS = [
  { value: 'referido', label: 'Referido' },
  { value: 'prospectacion', label: 'Prospectación directa' },
  { value: 'evento', label: 'Evento / Feria' },
  { value: 'web', label: 'Web / Inbound' },
  { value: 'aliado', label: 'Aliado comercial' },
  { value: 'otro', label: 'Otro' },
]

const TECNOLOGIA_OPTIONS = [
  { value: 'solar_fotovoltaica', label: 'Solar Fotovoltaica' },
  { value: 'eolica', label: 'Eólica' },
  { value: 'hidraulica', label: 'Hidráulica' },
  { value: 'biomasa', label: 'Biomasa' },
  { value: 'otro', label: 'Otro' },
]

const showTechnical = computed(() =>
  form.servicios.some((s) => ['representacion', 'cgm', 'monitoreo', 'ppa'].includes(s))
)

const showRecs = computed(() => form.servicios.includes('recs') || form.tipo_pipeline === 'recs')

const clienteOptions = computed(() => [
  ...clientesStore.clientes.map((c) => ({ value: String(c.id), label: c.nombre })),
])

const userOptions = computed(() => [
  { value: '', label: 'Sin asignar' },
  ...users.value.map((u) => ({
    value: String(u.id),
    label: u.first_name ? `${u.first_name} ${u.last_name || ''}`.trim() : u.username,
  })),
])

function toggleServicio(svc) {
  const idx = form.servicios.indexOf(svc)
  if (idx === -1) form.servicios.push(svc)
  else form.servicios.splice(idx, 1)
}

async function loadUsers() {
  try {
    const { data } = await api.get('/users/')
    users.value = data.results || data
  } catch {}
}

onMounted(async () => {
  await Promise.all([
    clientesStore.fetchClientes({ page_size: 200 }),
    loadUsers(),
  ])

  if (isEdit.value) {
    loading.value = true
    try {
      const deal = await dealsStore.fetchDeal(route.params.id)
      form.nombre = deal.nombre || ''
      form.cliente = String(deal.cliente?.id || deal.cliente || '')
      form.tipo_pipeline = deal.tipo_pipeline || 'servicios_principales'
      form.origen = deal.origen || ''
      form.servicios = deal.servicios || []
      form.comercial_asignado = String(deal.comercial_asignado?.id || deal.comercial_asignado || '')
      form.valor_estimado = deal.valor_estimado || ''
      form.fecha_estimada_cierre = deal.fecha_estimada_cierre || ''
      form.probabilidad = deal.probabilidad || 50
      if (deal.info_tecnica) {
        Object.assign(form, deal.info_tecnica)
      }
      if (deal.info_recs) {
        form.volumen_recs = deal.info_recs.volumen_recs || ''
        form.periodo_redencion = deal.info_recs.periodo_redencion || ''
        form.registro_irec = deal.info_recs.registro_irec || ''
      }
    } finally {
      loading.value = false
    }
  }
})

async function save() {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  if (!form.cliente) { error.value = 'El cliente es requerido'; return }

  saving.value = true
  error.value = ''

  const payload = {
    nombre: form.nombre,
    cliente: form.cliente,
    tipo_pipeline: form.tipo_pipeline,
    origen: form.origen,
    servicios: form.servicios,
    comercial_asignado: form.comercial_asignado || null,
    valor_estimado: form.valor_estimado || null,
    fecha_estimada_cierre: form.fecha_estimada_cierre || null,
    probabilidad: form.probabilidad,
  }

  if (showTechnical.value) {
    payload.info_tecnica = {
      nombre_proyecto: form.nombre_proyecto,
      tecnologia: form.tecnologia,
      capacidad_kwp: form.capacidad_kwp || null,
      generacion_mwh: form.generacion_mwh || null,
      latitud: form.latitud || null,
      longitud: form.longitud || null,
      operador_red: form.operador_red,
    }
  }

  if (showRecs.value) {
    payload.info_recs = {
      volumen_recs: form.volumen_recs || null,
      periodo_redencion: form.periodo_redencion,
      registro_irec: form.registro_irec,
    }
  }

  try {
    let result
    if (isEdit.value) {
      result = await dealsStore.updateDeal(route.params.id, payload)
    } else {
      result = await dealsStore.createDeal(payload)
    }
    router.push(`/deals/${result.id}`)
  } catch (e) {
    const data = e.response?.data
    if (data && typeof data === 'object') {
      error.value = Object.values(data).flat().join(' ')
    } else {
      error.value = 'Error al guardar el deal'
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto space-y-5">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <button
        class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        @click="router.push(isEdit ? `/deals/${route.params.id}` : '/deals')"
      >
        <ArrowLeft class="h-4 w-4" />
        {{ isEdit ? 'Volver al deal' : 'Deals' }}
      </button>
      <h1 class="text-2xl font-bold">{{ isEdit ? 'Editar Deal' : 'Nuevo Deal' }}</h1>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <Spinner size="xl" />
    </div>

    <template v-else>
      <div v-if="error" class="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive border border-destructive/20">
        {{ error }}
      </div>

      <!-- Section 1: Basic Info -->
      <Card>
        <CardHeader class="pb-3">
          <CardTitle>Información Básica</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-1.5">
            <Label>Nombre del deal *</Label>
            <Input v-model="form.nombre" placeholder="Ej: Representación Empresa Solar ABC" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <Label>Cliente *</Label>
              <Select v-model="form.cliente" :options="clienteOptions" placeholder="Seleccionar cliente..." />
            </div>
            <div class="space-y-1.5">
              <Label>Origen</Label>
              <Select v-model="form.origen" :options="ORIGEN_OPTIONS" placeholder="Seleccionar origen..." />
            </div>
          </div>

          <div class="space-y-2">
            <Label>Tipo de Pipeline</Label>
            <div class="flex gap-3">
              <label
                v-for="opt in [{ value: 'servicios_principales', label: 'Servicios Principales' }, { value: 'recs', label: 'RECs' }]"
                :key="opt.value"
                :class="[
                  'flex items-center gap-2 rounded-lg border px-4 py-3 cursor-pointer transition-all flex-1',
                  form.tipo_pipeline === opt.value
                    ? 'border-primary bg-primary/5 text-primary'
                    : 'border-border hover:border-primary/30',
                ]"
              >
                <input
                  type="radio"
                  :value="opt.value"
                  v-model="form.tipo_pipeline"
                  class="h-4 w-4 accent-primary"
                />
                <span class="text-sm font-medium">{{ opt.label }}</span>
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Section 2: Services -->
      <Card>
        <CardHeader class="pb-3">
          <CardTitle>Servicios</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <button
              v-for="svc in SERVICIOS_OPTIONS"
              :key="svc.value"
              type="button"
              :class="[
                'flex items-center justify-center rounded-lg border px-3 py-2.5 text-sm font-medium transition-all',
                form.servicios.includes(svc.value)
                  ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                  : 'border-border bg-background text-foreground hover:border-primary/40 hover:bg-muted/30',
              ]"
              @click="toggleServicio(svc.value)"
            >
              {{ svc.label }}
            </button>
          </div>
        </CardContent>
      </Card>

      <!-- Section 3: Commercial info -->
      <Card>
        <CardHeader class="pb-3">
          <CardTitle>Información Comercial</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <Label>Comercial Asignado</Label>
              <Select v-model="form.comercial_asignado" :options="userOptions" />
            </div>
            <div class="space-y-1.5">
              <Label>Valor Estimado (COP)</Label>
              <Input v-model="form.valor_estimado" type="number" placeholder="0" />
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <Label>Fecha Estimada de Cierre</Label>
              <Input v-model="form.fecha_estimada_cierre" type="date" />
            </div>
            <div class="space-y-1.5">
              <Label>Probabilidad (%): {{ form.probabilidad }}%</Label>
              <input
                v-model.number="form.probabilidad"
                type="range"
                min="0"
                max="100"
                step="5"
                class="w-full h-2 rounded-full accent-primary"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Section 4: Technical info (conditional) -->
      <Card v-if="showTechnical">
        <CardHeader class="pb-3">
          <CardTitle>Información Técnica</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <Label>Nombre del Proyecto</Label>
              <Input v-model="form.nombre_proyecto" placeholder="Ej: Planta Solar Norte" />
            </div>
            <div class="space-y-1.5">
              <Label>Tecnología</Label>
              <Select v-model="form.tecnologia" :options="TECNOLOGIA_OPTIONS" placeholder="Seleccionar..." />
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <Label>Capacidad (kWp)</Label>
              <Input v-model="form.capacidad_kwp" type="number" placeholder="0" />
            </div>
            <div class="space-y-1.5">
              <Label>Generación Estimada (MWh/año)</Label>
              <Input v-model="form.generacion_mwh" type="number" placeholder="0" />
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <Label>Latitud</Label>
              <Input v-model="form.latitud" placeholder="4.6097" />
            </div>
            <div class="space-y-1.5">
              <Label>Longitud</Label>
              <Input v-model="form.longitud" placeholder="-74.0817" />
            </div>
          </div>
          <div class="space-y-1.5">
            <Label>Operador de Red</Label>
            <Input v-model="form.operador_red" placeholder="Ej: ENEL, EPM, Codensa..." />
          </div>
        </CardContent>
      </Card>

      <!-- Section 5: RECs (conditional) -->
      <Card v-if="showRecs">
        <CardHeader class="pb-3">
          <CardTitle>Información RECs</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <Label>Volumen RECs (MWh)</Label>
              <Input v-model="form.volumen_recs" type="number" placeholder="0" />
            </div>
            <div class="space-y-1.5">
              <Label>Período de Redención</Label>
              <Input v-model="form.periodo_redencion" placeholder="Ej: 2024-2025" />
            </div>
          </div>
          <div class="space-y-1.5">
            <Label>Registro I-REC</Label>
            <Input v-model="form.registro_irec" placeholder="Número de registro I-REC" />
          </div>
        </CardContent>
      </Card>

      <!-- Actions -->
      <div class="flex items-center gap-3 pb-6">
        <Button
          variant="outline"
          @click="router.push(isEdit ? `/deals/${route.params.id}` : '/deals')"
        >
          Cancelar
        </Button>
        <Button :disabled="saving" @click="save">
          <Spinner v-if="saving" size="sm" class="mr-2" />
          <Save class="h-4 w-4 mr-1" />
          {{ isEdit ? 'Guardar Cambios' : 'Crear Deal' }}
        </Button>
      </div>
    </template>
  </div>
</template>
