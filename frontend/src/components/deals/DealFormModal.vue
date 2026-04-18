<script setup>
import { ref, reactive, watch } from 'vue'
import { useDealsStore } from '@/stores/deals'
import { useClientesStore } from '@/stores/clientes'
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import Spinner from '@/components/ui/Spinner.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  clienteId: { type: [Number, String], default: null },
  etapaInicial: { type: String, default: 'prospeccion' },
})

const emit = defineEmits(['created', 'update:open'])

const dealsStore = useDealsStore()
const clientesStore = useClientesStore()

const loading = ref(false)
const error = ref('')

const form = reactive({
  nombre: '',
  cliente: props.clienteId || '',
  tipo_pipeline: 'servicios_principales',
  servicios: [],
  etapa: props.etapaInicial,
  valor_estimado: '',
})

const SERVICIOS_OPTIONS = [
  { value: 'representacion', label: 'Representación' },
  { value: 'cgm', label: 'CGM' },
  { value: 'monitoreo', label: 'Monitoreo' },
  { value: 'ppa', label: 'PPA' },
  { value: 'venta_energia', label: 'Venta Energía' },
  { value: 'recs', label: 'RECs' },
]

const TIPO_OPTIONS = [
  { value: 'servicios_principales', label: 'Servicios Principales' },
  { value: 'recs', label: 'RECs' },
]

watch(
  () => props.open,
  (val) => {
    if (val) {
      clientesStore.fetchClientes()
      form.nombre = ''
      form.cliente = props.clienteId || ''
      form.tipo_pipeline = 'servicios_principales'
      form.servicios = []
      form.etapa = props.etapaInicial
      form.valor_estimado = ''
      error.value = ''
    }
  }
)

const clienteOptions = computed(() => [
  ...clientesStore.clientes.map((c) => ({ value: c.id, label: c.nombre }))
])

function toggleServicio(svc) {
  const idx = form.servicios.indexOf(svc)
  if (idx === -1) form.servicios.push(svc)
  else form.servicios.splice(idx, 1)
}

async function submit() {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  if (!form.cliente) { error.value = 'El cliente es requerido'; return }
  loading.value = true
  error.value = ''
  try {
    const payload = { ...form }
    if (payload.valor_estimado === '') delete payload.valor_estimado
    const data = await dealsStore.createDeal(payload)
    emit('created', data)
    emit('update:open', false)
  } catch (e) {
    error.value = e.response?.data?.detail || JSON.stringify(e.response?.data) || 'Error al crear el deal'
  } finally {
    loading.value = false
  }
}
</script>

<script>
import { computed } from 'vue'
export default { name: 'DealFormModal' }
</script>

<template>
  <Dialog :open="open" size="md" @update:open="emit('update:open', $event)">
    <DialogHeader>
      <DialogTitle>Nuevo Deal</DialogTitle>
    </DialogHeader>

    <div class="px-6 pb-4 space-y-4">
      <div v-if="error" class="rounded-md bg-destructive/10 px-4 py-2 text-sm text-destructive">
        {{ error }}
      </div>

      <div class="space-y-1.5">
        <Label>Nombre del deal *</Label>
        <Input v-model="form.nombre" placeholder="Ej: Representación Empresa XYZ" />
      </div>

      <div class="space-y-1.5">
        <Label>Cliente *</Label>
        <Select
          v-model="form.cliente"
          :options="clienteOptions"
          placeholder="Seleccionar cliente..."
        />
      </div>

      <div class="space-y-1.5">
        <Label>Tipo de Pipeline</Label>
        <Select v-model="form.tipo_pipeline" :options="TIPO_OPTIONS" />
      </div>

      <div class="space-y-1.5">
        <Label>Servicios</Label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="svc in SERVICIOS_OPTIONS"
            :key="svc.value"
            type="button"
            :class="[
              'rounded-full border px-3 py-1 text-xs font-medium transition-all',
              form.servicios.includes(svc.value)
                ? 'border-primary bg-primary text-primary-foreground'
                : 'border-input bg-background text-muted-foreground hover:border-primary/50',
            ]"
            @click="toggleServicio(svc.value)"
          >
            {{ svc.label }}
          </button>
        </div>
      </div>

      <div class="space-y-1.5">
        <Label>Valor Estimado (COP)</Label>
        <Input v-model="form.valor_estimado" type="number" placeholder="0" />
      </div>
    </div>

    <DialogFooter>
      <Button variant="outline" @click="emit('update:open', false)">Cancelar</Button>
      <Button :disabled="loading" @click="submit">
        <Spinner v-if="loading" size="sm" class="mr-2" />
        Crear Deal
      </Button>
    </DialogFooter>
  </Dialog>
</template>
