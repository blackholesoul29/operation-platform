<script setup>
import { onMounted, ref, computed, reactive, watch } from 'vue'
import { useTareasStore } from '@/stores/tareas'
import { useClientesStore } from '@/stores/clientes'
import { useDealsStore } from '@/stores/deals'
import api from '@/lib/api'
import { Plus, CheckSquare, Clock } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Select from '@/components/ui/Select.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import Sheet from '@/components/ui/Sheet.vue'
import TareaItem from '@/components/tareas/TareaItem.vue'

const tareasStore = useTareasStore()
const clientesStore = useClientesStore()
const dealsStore = useDealsStore()

const activeTab = ref('pendientes')
const sheetOpen = ref(false)
const editingTarea = ref(null)
const saving = ref(false)
const formError = ref('')
const users = ref([])

const form = reactive({
  titulo: '',
  descripcion: '',
  deal: '',
  cliente: '',
  asignado_a: '',
  fecha_limite: '',
  prioridad: 'media',
})

const PRIORIDAD_OPTIONS = [
  { value: 'baja', label: 'Baja' },
  { value: 'media', label: 'Media' },
  { value: 'alta', label: 'Alta' },
  { value: 'urgente', label: 'Urgente' },
]

onMounted(async () => {
  await Promise.all([
    tareasStore.fetchTareas(),
    clientesStore.fetchClientes({ page_size: 200 }),
    dealsStore.fetchDeals({ page_size: 200 }),
    loadUsers(),
  ])
})

async function loadUsers() {
  try {
    const { data } = await api.get('/users/')
    users.value = data.results || data
  } catch {}
}

const tareasPendientes = computed(() => tareasStore.tareas.filter(t => !t.completada))
const tareasCompletadas = computed(() => tareasStore.tareas.filter(t => t.completada))

const clienteOptions = computed(() => [
  { value: '', label: 'Sin cliente' },
  ...clientesStore.clientes.map(c => ({ value: String(c.id), label: c.nombre })),
])

const dealOptions = computed(() => [
  { value: '', label: 'Sin deal' },
  ...dealsStore.deals.map(d => ({ value: String(d.id), label: d.nombre })),
])

const userOptions = computed(() => [
  { value: '', label: 'Sin asignar' },
  ...users.value.map(u => ({
    value: String(u.id),
    label: u.first_name ? `${u.first_name} ${u.last_name || ''}`.trim() : u.username,
  })),
])

function openCreate() {
  editingTarea.value = null
  Object.assign(form, { titulo: '', descripcion: '', deal: '', cliente: '', asignado_a: '', fecha_limite: '', prioridad: 'media' })
  formError.value = ''
  sheetOpen.value = true
}

function openEdit(tarea) {
  editingTarea.value = tarea
  Object.assign(form, {
    titulo: tarea.titulo || '',
    descripcion: tarea.descripcion || '',
    deal: String(tarea.deal?.id || tarea.deal || ''),
    cliente: String(tarea.cliente?.id || tarea.cliente || ''),
    asignado_a: String(tarea.asignado_a?.id || tarea.asignado_a || ''),
    fecha_limite: tarea.fecha_limite || '',
    prioridad: tarea.prioridad || 'media',
  })
  formError.value = ''
  sheetOpen.value = true
}

async function saveTarea() {
  if (!form.titulo.trim()) { formError.value = 'El título es requerido'; return }
  saving.value = true
  formError.value = ''
  const payload = {
    titulo: form.titulo,
    descripcion: form.descripcion,
    prioridad: form.prioridad,
    deal: form.deal || null,
    cliente: form.cliente || null,
    asignado_a: form.asignado_a || null,
    fecha_limite: form.fecha_limite || null,
  }
  try {
    if (editingTarea.value) {
      await tareasStore.updateTarea(editingTarea.value.id, payload)
    } else {
      await tareasStore.createTarea(payload)
    }
    sheetOpen.value = false
  } catch (e) {
    formError.value = e.response?.data ? Object.values(e.response.data).flat().join(' ') : 'Error al guardar'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center gap-3">
      <h1 class="text-2xl font-bold flex-1">Tareas</h1>
      <Button @click="openCreate">
        <Plus class="h-4 w-4" />
        Nueva Tarea
      </Button>
    </div>

    <!-- Tabs -->
    <div class="flex border-b gap-1">
      <button
        v-for="tab in [{key:'pendientes', label:`Pendientes (${tareasPendientes.length})`}, {key:'completadas', label:`Completadas (${tareasCompletadas.length})`}]"
        :key="tab.key"
        :class="['px-4 py-2.5 text-sm font-medium border-b-2 transition-colors', activeTab===tab.key ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground']"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="tareasStore.loading" class="flex justify-center py-12"><Spinner size="lg" /></div>

    <!-- Pendientes -->
    <div v-else-if="activeTab === 'pendientes'">
      <EmptyState
        v-if="!tareasPendientes.length"
        :icon="CheckSquare"
        title="Sin tareas pendientes"
        description="¡Estás al día! No tienes tareas pendientes."
      />
      <div v-else class="space-y-2">
        <TareaItem
          v-for="tarea in tareasPendientes"
          :key="tarea.id"
          :tarea="tarea"
          @edit="openEdit"
        />
      </div>
    </div>

    <!-- Completadas -->
    <div v-else-if="activeTab === 'completadas'">
      <EmptyState
        v-if="!tareasCompletadas.length"
        :icon="CheckSquare"
        title="Sin tareas completadas"
        description="Las tareas completadas aparecerán aquí."
      />
      <div v-else class="space-y-2">
        <TareaItem
          v-for="tarea in tareasCompletadas"
          :key="tarea.id"
          :tarea="tarea"
          @edit="openEdit"
        />
      </div>
    </div>

    <!-- Sheet: Create/Edit tarea -->
    <Sheet :open="sheetOpen" :title="editingTarea ? 'Editar Tarea' : 'Nueva Tarea'" @update:open="sheetOpen = $event">
      <div class="space-y-4">
        <div v-if="formError" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{{ formError }}</div>

        <div class="space-y-1.5">
          <Label>Título *</Label>
          <Input v-model="form.titulo" placeholder="Ej: Enviar propuesta comercial" />
        </div>

        <div class="space-y-1.5">
          <Label>Descripción</Label>
          <Textarea v-model="form.descripcion" placeholder="Detalle de la tarea..." />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-1.5">
            <Label>Prioridad</Label>
            <Select v-model="form.prioridad" :options="PRIORIDAD_OPTIONS" />
          </div>
          <div class="space-y-1.5">
            <Label>Fecha Límite</Label>
            <Input v-model="form.fecha_limite" type="date" />
          </div>
        </div>

        <div class="space-y-1.5">
          <Label>Deal (opcional)</Label>
          <Select v-model="form.deal" :options="dealOptions" />
        </div>

        <div class="space-y-1.5">
          <Label>Cliente (opcional)</Label>
          <Select v-model="form.cliente" :options="clienteOptions" />
        </div>

        <div class="space-y-1.5">
          <Label>Asignado a</Label>
          <Select v-model="form.asignado_a" :options="userOptions" />
        </div>

        <div class="flex gap-3 pt-2">
          <Button variant="outline" class="flex-1" @click="sheetOpen = false">Cancelar</Button>
          <Button class="flex-1" :disabled="saving" @click="saveTarea">
            <Spinner v-if="saving" size="sm" class="mr-2" />
            {{ editingTarea ? 'Guardar' : 'Crear Tarea' }}
          </Button>
        </div>
      </div>
    </Sheet>
  </div>
</template>
