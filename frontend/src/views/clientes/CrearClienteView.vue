<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useClientesStore } from '@/stores/clientes'
import { Plus, Search, Edit, Trash2, ExternalLink, Upload, X } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import Badge from '@/components/ui/Badge.vue'
import Spinner from '@/components/ui/Spinner.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const store = useClientesStore()

const search = ref('')
const showCreateModal = ref(false)
const showEditPanel = ref(false)
const editingCliente = ref(null)
const creating = ref(false)
const saving = ref(false)
const createError = ref('')
const saveError = ref('')
const confirmDelete = ref(false)
const deletingId = ref(null)
const deleteLoading = ref(false)

const SERVICIOS = ['CGM', 'Representación', 'Operación', 'PPA']

const ESTADOS = [
  { value: 'Originación', label: 'Originación' },
  { value: 'Negociación', label: 'Negociación' },
  { value: 'Cierre', label: 'Cierre' },
]

const DOCS = [
  { key: 'razon_social', label: 'Razón Social' },
  { key: 'nit', label: 'NIT' },
  { key: 'rut', label: 'RUT del cliente' },
  { key: 'camara_comercio', label: 'Cámara de Comercio' },
  { key: 'nda', label: 'NDA' },
  { key: 'oferta', label: 'Oferta' },
  { key: 'cert_bancaria', label: 'Certificación Bancaria' },
]

const PERIODOS = [
  { value: '1', label: '1 año' },
  { value: '2', label: '2 años' },
  { value: '3', label: '3 años' },
  { value: '4', label: '4 años' },
  { value: '5', label: '5 años' },
  { value: '10', label: '10 años' },
]

const createForm = reactive({ nombre_comercial: '', estado: 'Originación', servicios: [] })
const editForm = reactive({
  nombre_comercial: '',
  estado: 'Originación',
  servicios: [],
  fecha_inicio: '',
  fecha_fin: '',
  renovacion_automatica: false,
  periodo_renovacion: '',
})

onMounted(() => store.fetchClientes())

const filteredClientes = computed(() => {
  if (!search.value) return store.clientes
  const q = search.value.toLowerCase()
  return store.clientes.filter(c =>
    c.nombre_comercial?.toLowerCase().includes(q) ||
    (Array.isArray(c.servicios) ? c.servicios : []).join(' ').toLowerCase().includes(q)
  )
})

function toggleServicio(form, s) {
  const idx = form.servicios.indexOf(s)
  if (idx >= 0) form.servicios.splice(idx, 1)
  else form.servicios.push(s)
}

function openCreate() {
  Object.assign(createForm, { nombre_comercial: '', estado: 'Originación', servicios: [] })
  createError.value = ''
  showCreateModal.value = true
}

async function doCreate() {
  if (!createForm.nombre_comercial.trim()) { createError.value = 'El nombre comercial es requerido'; return }
  creating.value = true
  createError.value = ''
  try {
    await store.createCliente({ ...createForm, servicios: [...createForm.servicios] })
    showCreateModal.value = false
  } catch (e) {
    createError.value = e.message || 'Error al crear el cliente'
  } finally {
    creating.value = false
  }
}

function openEdit(cliente) {
  editingCliente.value = { ...cliente }
  Object.assign(editForm, {
    nombre_comercial:      cliente.nombre_comercial || '',
    estado:                cliente.estado || 'Originación',
    servicios:             Array.isArray(cliente.servicios) ? [...cliente.servicios] : [],
    fecha_inicio:          cliente.fecha_inicio || '',
    fecha_fin:             cliente.fecha_fin || '',
    renovacion_automatica: cliente.renovacion_automatica === 'TRUE' || cliente.renovacion_automatica === true,
    periodo_renovacion:    cliente.periodo_renovacion || '',
  })
  saveError.value = ''
  showEditPanel.value = true
}

// Mantener el panel sincronizado cuando el store actualiza el cliente
function syncEditingCliente() {
  if (!editingCliente.value) return
  const updated = store.clientes.find(c => c.id === editingCliente.value.id)
  if (updated) editingCliente.value = { ...updated }
}

async function doSave() {
  if (!editForm.nombre_comercial.trim()) { saveError.value = 'El nombre es requerido'; return }
  saving.value = true
  saveError.value = ''
  try {
    await store.updateCliente(editingCliente.value.id, {
      nombre_comercial:      editForm.nombre_comercial,
      estado:                editForm.estado,
      servicios:             [...editForm.servicios],
      fecha_inicio:          editForm.fecha_inicio,
      fecha_fin:             editForm.fecha_fin,
      renovacion_automatica: editForm.renovacion_automatica ? 'TRUE' : 'FALSE',
      periodo_renovacion:    editForm.renovacion_automatica ? editForm.periodo_renovacion : '',
    })
    syncEditingCliente()
  } catch (e) {
    saveError.value = e.message || 'Error al guardar'
  } finally {
    saving.value = false
  }
}

async function handleFileUpload(fieldKey, event) {
  const file = event.target.files?.[0]
  if (!file || !editingCliente.value) return
  saveError.value = ''
  try {
    await store.uploadFile(editingCliente.value.id, fieldKey, file)
    syncEditingCliente()
  } catch (e) {
    saveError.value = `Error subiendo archivo: ${e.message}`
  }
  event.target.value = ''
}

function openDelete(id) { deletingId.value = id; confirmDelete.value = true }

async function doDelete() {
  deleteLoading.value = true
  try {
    await store.deleteCliente(deletingId.value)
    confirmDelete.value = false
    if (editingCliente.value?.id === deletingId.value) showEditPanel.value = false
  } catch (e) {
    saveError.value = e.message
  } finally {
    deleteLoading.value = false
  }
}

const estadoClass = (e) => ({
  Originación: 'bg-amber-100 text-amber-800',
  Negociación: 'bg-blue-100 text-blue-800',
  Cierre: 'bg-green-100 text-green-800',
}[e] || 'bg-slate-100 text-slate-700')

const ALL_DOC_KEYS = [...DOCS.map(d => d.key), 'contrato']
const docsCount = (c) => ALL_DOC_KEYS.filter(k => c[`${k}_url`]).length
</script>

<template>
  <div class="space-y-4">

    <!-- Header -->
    <div class="flex items-center gap-3">
      <h1 class="text-2xl font-bold flex-1">Creación de Clientes</h1>
      <Button @click="openCreate">
        <Plus class="h-4 w-4 mr-1" /> Nuevo Cliente
      </Button>
    </div>

    <!-- Buscador -->
    <div class="relative max-w-xs">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input v-model="search" placeholder="Buscar cliente..." class="pl-9" />
    </div>

    <!-- Tabla -->
    <div class="rounded-xl border bg-card shadow-sm overflow-hidden">
      <div v-if="store.loading" class="flex justify-center py-16"><Spinner size="lg" /></div>
      <div v-else-if="store.error" class="text-center py-12 text-sm text-destructive">{{ store.error }}</div>
      <div v-else-if="!filteredClientes.length" class="text-center py-12 text-sm text-muted-foreground">
        No hay clientes registrados aún.
      </div>
      <table v-else class="w-full">
        <thead class="border-b bg-slate-50/80">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wide">Nombre Comercial</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wide">Servicios</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wide">Estado</th>
            <th class="px-4 py-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wide">Docs</th>
            <th class="px-4 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wide">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="c in filteredClientes"
            :key="c.id"
            class="border-b last:border-0 hover:bg-slate-50/50 transition-colors"
          >
            <td class="px-4 py-3">
              <div class="flex items-center gap-2.5">
                <div class="h-8 w-8 flex-shrink-0 rounded-lg bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
                  {{ c.nombre_comercial?.slice(0, 2).toUpperCase() || '?' }}
                </div>
                <span class="font-medium text-sm">{{ c.nombre_comercial }}</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="s in (Array.isArray(c.servicios) ? c.servicios : [])"
                  :key="s"
                  class="px-2 py-0.5 text-xs rounded-full bg-primary/10 text-primary font-medium"
                >{{ s }}</span>
                <span v-if="!c.servicios?.length" class="text-xs text-muted-foreground">—</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <span :class="['px-2.5 py-1 text-xs font-semibold rounded-full', estadoClass(c.estado)]">
                {{ c.estado || '—' }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <span class="text-xs font-medium text-muted-foreground">{{ docsCount(c) }}/{{ ALL_DOC_KEYS.length }}</span>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center justify-end gap-1">
                <button
                  class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                  title="Editar"
                  @click="openEdit(c)"
                >
                  <Edit class="h-4 w-4" />
                </button>
                <button
                  class="p-1.5 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                  title="Eliminar"
                  @click="openDelete(c.id)"
                >
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ─── Modal: Crear cliente ─── -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40" @click="showCreateModal = false" />
        <div class="relative z-10 bg-background rounded-xl shadow-xl w-full max-w-md p-6">
          <div class="flex items-center justify-between mb-5">
            <h2 class="text-lg font-semibold">Nuevo Cliente</h2>
            <button @click="showCreateModal = false" class="text-muted-foreground hover:text-foreground">
              <X class="h-5 w-5" />
            </button>
          </div>

          <div class="space-y-4">
            <div v-if="createError" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{{ createError }}</div>

            <div class="space-y-1.5">
              <Label>Nombre comercial *</Label>
              <Input
                v-model="createForm.nombre_comercial"
                placeholder="Nombre comercial de la empresa"
                autofocus
                @keyup.enter="doCreate"
              />
            </div>

            <div class="space-y-1.5">
              <Label>Estado del deal</Label>
              <Select v-model="createForm.estado" :options="ESTADOS" />
            </div>

            <div class="space-y-1.5">
              <Label>Servicios</Label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="s in SERVICIOS"
                  :key="s"
                  type="button"
                  :class="[
                    'px-3 py-1.5 text-sm rounded-lg border transition-colors',
                    createForm.servicios.includes(s)
                      ? 'bg-primary text-white border-primary'
                      : 'bg-background border-border text-foreground hover:bg-accent',
                  ]"
                  @click="toggleServicio(createForm, s)"
                >{{ s }}</button>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <Button variant="outline" @click="showCreateModal = false">Cancelar</Button>
            <Button :disabled="creating" @click="doCreate">
              <Spinner v-if="creating" size="sm" class="mr-2" />
              {{ creating ? 'Creando...' : 'Crear cliente' }}
            </Button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── Panel: Editar cliente ─── -->
    <Teleport to="body">
      <div v-if="showEditPanel && editingCliente" class="fixed inset-0 z-50 flex justify-end">
        <div class="absolute inset-0 bg-black/30" @click="showEditPanel = false" />
        <div class="relative z-10 bg-background w-full max-w-lg h-full flex flex-col shadow-2xl">

          <!-- Header del panel -->
          <div class="flex items-center justify-between px-6 py-4 border-b flex-shrink-0">
            <div class="min-w-0">
              <h2 class="text-base font-semibold truncate">{{ editingCliente.nombre_comercial }}</h2>
              <a
                v-if="editingCliente.folder_url"
                :href="editingCliente.folder_url"
                target="_blank"
                class="text-xs text-primary hover:underline flex items-center gap-1 mt-0.5"
              >
                <ExternalLink class="h-3 w-3" /> Abrir carpeta en Drive
              </a>
            </div>
            <button @click="showEditPanel = false" class="ml-4 p-1 text-muted-foreground hover:text-foreground flex-shrink-0">
              <X class="h-5 w-5" />
            </button>
          </div>

          <!-- Contenido scrolleable -->
          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <div v-if="saveError" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{{ saveError }}</div>

            <!-- Sección: Información básica -->
            <section class="space-y-4">
              <h3 class="text-sm font-semibold border-b pb-2">Información básica</h3>

              <div class="space-y-1.5">
                <Label>Nombre comercial *</Label>
                <Input v-model="editForm.nombre_comercial" />
              </div>

              <div class="space-y-1.5">
                <Label>Estado del deal</Label>
                <Select v-model="editForm.estado" :options="ESTADOS" />
              </div>

              <div class="space-y-1.5">
                <Label>Servicios</Label>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="s in SERVICIOS"
                    :key="s"
                    type="button"
                    :class="[
                      'px-3 py-1.5 text-sm rounded-lg border transition-colors',
                      editForm.servicios.includes(s)
                        ? 'bg-primary text-white border-primary'
                        : 'bg-background border-border text-foreground hover:bg-accent',
                    ]"
                    @click="toggleServicio(editForm, s)"
                  >{{ s }}</button>
                </div>
              </div>

              <Button size="sm" :disabled="saving" @click="doSave">
                <Spinner v-if="saving" size="sm" class="mr-2" />
                {{ saving ? 'Guardando...' : 'Guardar cambios' }}
              </Button>
            </section>

            <!-- Sección: Contrato del servicio -->
            <section class="space-y-4">
              <h3 class="text-sm font-semibold border-b pb-2">Contrato del servicio</h3>

              <!-- Archivo del contrato -->
              <div class="flex items-center justify-between">
                <div class="min-w-0 flex-1 mr-3">
                  <p class="text-sm font-medium">Contrato</p>
                  <a
                    v-if="editingCliente.contrato_url"
                    :href="editingCliente.contrato_url"
                    target="_blank"
                    class="text-xs text-primary hover:underline flex items-center gap-1 mt-0.5"
                  >
                    <ExternalLink class="h-3 w-3" /> Ver contrato
                  </a>
                  <p v-else class="text-xs text-muted-foreground mt-0.5">Sin archivo</p>
                </div>
                <span v-if="store.isUploading(editingCliente.id, 'contrato')" class="flex items-center gap-1.5 text-xs text-muted-foreground px-3">
                  <Spinner size="sm" /> Subiendo...
                </span>
                <label v-else class="cursor-pointer flex-shrink-0">
                  <input type="file" class="hidden" @change="handleFileUpload('contrato', $event)" />
                  <span class="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-accent transition-colors select-none">
                    <Upload class="h-3 w-3" />
                    {{ editingCliente.contrato_url ? 'Cambiar' : 'Subir' }}
                  </span>
                </label>
              </div>

              <!-- Fechas -->
              <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1.5">
                  <Label>Fecha inicio</Label>
                  <Input v-model="editForm.fecha_inicio" type="date" />
                </div>
                <div class="space-y-1.5">
                  <Label>Fecha fin</Label>
                  <Input v-model="editForm.fecha_fin" type="date" />
                </div>
              </div>

              <!-- Renovación automática -->
              <div class="space-y-3">
                <div class="flex items-center gap-3">
                  <button
                    type="button"
                    :class="[
                      'relative h-5 w-9 rounded-full transition-colors flex-shrink-0',
                      editForm.renovacion_automatica ? 'bg-primary' : 'bg-slate-200',
                    ]"
                    @click="editForm.renovacion_automatica = !editForm.renovacion_automatica"
                  >
                    <span
                      :class="[
                        'absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform',
                        editForm.renovacion_automatica ? 'translate-x-4' : 'translate-x-0',
                      ]"
                    />
                  </button>
                  <span class="text-sm font-medium">Renovación automática</span>
                </div>

                <div v-if="editForm.renovacion_automatica" class="space-y-1.5 pl-12">
                  <Label>Período de renovación</Label>
                  <Select v-model="editForm.periodo_renovacion" :options="PERIODOS" placeholder="Seleccionar..." />
                </div>
              </div>

              <Button size="sm" :disabled="saving" @click="doSave">
                <Spinner v-if="saving" size="sm" class="mr-2" />
                {{ saving ? 'Guardando...' : 'Guardar contrato' }}
              </Button>
            </section>

            <!-- Sección: Documentos -->
            <section class="space-y-1">
              <h3 class="text-sm font-semibold border-b pb-2 mb-3">Documentos</h3>
              <div
                v-for="doc in DOCS"
                :key="doc.key"
                class="flex items-center justify-between py-3 border-b border-dashed border-slate-100 last:border-0"
              >
                <div class="min-w-0 flex-1 mr-3">
                  <p class="text-sm font-medium">{{ doc.label }}</p>
                  <a
                    v-if="editingCliente[`${doc.key}_url`]"
                    :href="editingCliente[`${doc.key}_url`]"
                    target="_blank"
                    class="text-xs text-primary hover:underline flex items-center gap-1 mt-0.5"
                  >
                    <ExternalLink class="h-3 w-3" /> Ver archivo
                  </a>
                  <p v-else class="text-xs text-muted-foreground mt-0.5">Sin archivo</p>
                </div>

                <!-- Spinner mientras sube -->
                <span
                  v-if="store.isUploading(editingCliente.id, doc.key)"
                  class="flex items-center gap-1.5 text-xs text-muted-foreground px-3"
                >
                  <Spinner size="sm" /> Subiendo...
                </span>

                <!-- Botón subir (label que activa el file input) -->
                <label v-else class="cursor-pointer flex-shrink-0">
                  <input
                    type="file"
                    class="hidden"
                    @change="handleFileUpload(doc.key, $event)"
                  />
                  <span class="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-accent transition-colors select-none">
                    <Upload class="h-3 w-3" />
                    {{ editingCliente[`${doc.key}_url`] ? 'Cambiar' : 'Subir' }}
                  </span>
                </label>
              </div>
            </section>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Confirmar eliminación -->
    <ConfirmDialog
      :open="confirmDelete"
      title="Eliminar cliente"
      description="Se eliminará el cliente y su carpeta de Drive permanentemente. Esta acción no se puede deshacer."
      confirm-label="Eliminar"
      :destructive="true"
      :loading="deleteLoading"
      @update:open="confirmDelete = $event"
      @confirm="doDelete"
      @cancel="confirmDelete = false"
    />
  </div>
</template>
