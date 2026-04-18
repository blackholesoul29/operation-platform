<script setup>
import { onMounted, ref, computed, watch, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useClientesStore } from '@/stores/clientes'
import {
  Plus, Search, Eye, Edit, Trash2, ChevronLeft, ChevronRight, Building2, X
} from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import Table from '@/components/ui/Table.vue'
import TableHeader from '@/components/ui/TableHeader.vue'
import TableBody from '@/components/ui/TableBody.vue'
import TableRow from '@/components/ui/TableRow.vue'
import TableHead from '@/components/ui/TableHead.vue'
import TableCell from '@/components/ui/TableCell.vue'
import Badge from '@/components/ui/Badge.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const router = useRouter()
const store = useClientesStore()

const search = ref('')
const segmentoFilter = ref('')
const page = ref(1)
const pageSize = 15

const showModal = ref(false)
const editingId = ref(null)
const saving = ref(false)
const formError = ref('')

const confirmDelete = ref(false)
const deletingId = ref(null)
const deleteLoading = ref(false)

const form = reactive({
  nombre: '',
  nit: '',
  segmento: '',
  ciudad: '',
  direccion: '',
  website: '',
  telefono: '',
  email_contacto: '',
})

const SEGMENTO_OPTIONS = [
  { value: '', label: 'Todos los segmentos' },
  { value: 'gran_consumidor', label: 'Gran Consumidor' },
  { value: 'generador', label: 'Generador' },
  { value: 'comercializador', label: 'Comercializador' },
  { value: 'autogenerador', label: 'Autogenerador' },
  { value: 'otro', label: 'Otro' },
]

const SEGMENTO_FORM_OPTIONS = SEGMENTO_OPTIONS.filter(o => o.value)

function buildParams() {
  const p = { page: page.value, page_size: pageSize }
  if (search.value) p.search = search.value
  if (segmentoFilter.value) p.segmento = segmentoFilter.value
  return p
}

async function load() { await store.fetchClientes(buildParams()) }

onMounted(load)
watch([search, segmentoFilter], () => { page.value = 1; load() })
watch(page, load)

const totalPages = computed(() => Math.ceil(store.total / pageSize))

function openCreate() {
  editingId.value = null
  Object.assign(form, { nombre: '', nit: '', segmento: '', ciudad: '', direccion: '', website: '', telefono: '', email_contacto: '' })
  formError.value = ''
  showModal.value = true
}

function openEdit(cliente) {
  editingId.value = cliente.id
  Object.assign(form, {
    nombre: cliente.nombre || '',
    nit: cliente.nit || '',
    segmento: cliente.segmento || '',
    ciudad: cliente.ciudad || '',
    direccion: cliente.direccion || '',
    website: cliente.website || '',
    telefono: cliente.telefono || '',
    email_contacto: cliente.email_contacto || '',
  })
  formError.value = ''
  showModal.value = true
}

async function saveCliente() {
  if (!form.nombre.trim()) { formError.value = 'El nombre es requerido'; return }
  saving.value = true
  formError.value = ''
  try {
    if (editingId.value) {
      await store.updateCliente(editingId.value, { ...form })
    } else {
      await store.createCliente({ ...form })
    }
    showModal.value = false
    load()
  } catch (e) {
    const d = e.response?.data
    formError.value = typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Error al guardar'
  } finally {
    saving.value = false
  }
}

function openDelete(id) { deletingId.value = id; confirmDelete.value = true }

async function doDelete() {
  deleteLoading.value = true
  try { await store.deleteCliente(deletingId.value); confirmDelete.value = false }
  finally { deleteLoading.value = false }
}

const segmentoLabel = (v) => SEGMENTO_OPTIONS.find(o => o.value === v)?.label || v || '—'
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center gap-3">
      <h1 class="text-2xl font-bold flex-1">Clientes</h1>
      <Button @click="openCreate">
        <Plus class="h-4 w-4" />
        Nuevo Cliente
      </Button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-[200px] max-w-xs">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input v-model="search" placeholder="Buscar por nombre o NIT..." class="pl-9" />
      </div>
      <Select v-model="segmentoFilter" :options="SEGMENTO_OPTIONS" class="w-48" />
    </div>

    <!-- Table -->
    <div class="rounded-xl border bg-card shadow-sm overflow-hidden">
      <div v-if="store.loading" class="flex justify-center py-16">
        <Spinner size="lg" />
      </div>
      <EmptyState
        v-else-if="!store.clientes.length"
        :icon="Building2"
        title="No hay clientes"
        description="Crea el primer cliente para comenzar."
      />
      <Table v-else>
        <TableHeader>
          <TableRow>
            <TableHead>Nombre</TableHead>
            <TableHead>NIT</TableHead>
            <TableHead>Segmento</TableHead>
            <TableHead>Ciudad</TableHead>
            <TableHead class="text-center">Deals activos</TableHead>
            <TableHead class="text-right">Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="c in store.clientes"
            :key="c.id"
            class="cursor-pointer"
            @click="router.push(`/clientes/${c.id}`)"
          >
            <TableCell>
              <div class="flex items-center gap-2.5">
                <div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-primary/10 text-xs font-bold text-primary">
                  {{ c.nombre?.slice(0, 2).toUpperCase() }}
                </div>
                <span class="font-medium">{{ c.nombre }}</span>
              </div>
            </TableCell>
            <TableCell class="text-muted-foreground text-sm">{{ c.nit || '—' }}</TableCell>
            <TableCell>
              <Badge v-if="c.segmento" variant="secondary">{{ segmentoLabel(c.segmento) }}</Badge>
              <span v-else class="text-muted-foreground text-sm">—</span>
            </TableCell>
            <TableCell class="text-sm text-muted-foreground">{{ c.ciudad || '—' }}</TableCell>
            <TableCell class="text-center">
              <span class="text-sm font-medium">{{ c.deals_activos ?? 0 }}</span>
            </TableCell>
            <TableCell class="text-right" @click.stop>
              <div class="flex items-center justify-end gap-1">
                <button class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors" @click="router.push(`/clientes/${c.id}`)">
                  <Eye class="h-4 w-4" />
                </button>
                <button class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors" @click="openEdit(c)">
                  <Edit class="h-4 w-4" />
                </button>
                <button class="p-1.5 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors" @click="openDelete(c.id)">
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between text-sm text-muted-foreground">
      <span>{{ (page-1)*pageSize+1 }}–{{ Math.min(page*pageSize, store.total) }} de {{ store.total }}</span>
      <div class="flex items-center gap-1">
        <Button variant="outline" size="icon" :disabled="page<=1" @click="page--"><ChevronLeft class="h-4 w-4"/></Button>
        <span class="px-3 py-1 text-sm font-medium">{{ page }}/{{ totalPages }}</span>
        <Button variant="outline" size="icon" :disabled="page>=totalPages" @click="page++"><ChevronRight class="h-4 w-4"/></Button>
      </div>
    </div>

    <!-- Create/Edit modal -->
    <Dialog :open="showModal" size="md" @update:open="showModal = $event">
      <DialogHeader>
        <DialogTitle>{{ editingId ? 'Editar Cliente' : 'Nuevo Cliente' }}</DialogTitle>
      </DialogHeader>
      <div class="px-6 pb-4 space-y-4">
        <div v-if="formError" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{{ formError }}</div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1.5 col-span-2">
            <Label>Nombre *</Label>
            <Input v-model="form.nombre" placeholder="Razón social o nombre comercial" />
          </div>
          <div class="space-y-1.5">
            <Label>NIT</Label>
            <Input v-model="form.nit" placeholder="900.123.456-7" />
          </div>
          <div class="space-y-1.5">
            <Label>Segmento</Label>
            <Select v-model="form.segmento" :options="SEGMENTO_FORM_OPTIONS" placeholder="Seleccionar..." />
          </div>
          <div class="space-y-1.5">
            <Label>Ciudad</Label>
            <Input v-model="form.ciudad" placeholder="Bogotá" />
          </div>
          <div class="space-y-1.5">
            <Label>Teléfono</Label>
            <Input v-model="form.telefono" placeholder="+57 300 000 0000" />
          </div>
          <div class="space-y-1.5">
            <Label>Email de Contacto</Label>
            <Input v-model="form.email_contacto" type="email" placeholder="contacto@empresa.com" />
          </div>
          <div class="space-y-1.5">
            <Label>Website</Label>
            <Input v-model="form.website" placeholder="https://empresa.com" />
          </div>
          <div class="space-y-1.5 col-span-2">
            <Label>Dirección</Label>
            <Input v-model="form.direccion" placeholder="Calle 100 # 50-20" />
          </div>
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="showModal = false">Cancelar</Button>
        <Button :disabled="saving" @click="saveCliente">
          <Spinner v-if="saving" size="sm" class="mr-2" />
          {{ editingId ? 'Guardar Cambios' : 'Crear Cliente' }}
        </Button>
      </DialogFooter>
    </Dialog>

    <ConfirmDialog
      :open="confirmDelete"
      title="Eliminar Cliente"
      description="Se eliminarán todos los datos del cliente permanentemente."
      confirm-label="Eliminar"
      :destructive="true"
      :loading="deleteLoading"
      @update:open="confirmDelete = $event"
      @confirm="doDelete"
      @cancel="confirmDelete = false"
    />
  </div>
</template>
