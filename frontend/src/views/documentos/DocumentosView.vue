<script setup>
import { onMounted, ref, computed, watch, reactive } from 'vue'
import { useDocumentosStore } from '@/stores/documentos'
import { useClientesStore } from '@/stores/clientes'
import { useDealsStore } from '@/stores/deals'
import {
  Plus, Search, Trash2, Eye, FolderOpen, Download, ChevronLeft, ChevronRight
} from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import Badge from '@/components/ui/Badge.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import Table from '@/components/ui/Table.vue'
import TableHeader from '@/components/ui/TableHeader.vue'
import TableBody from '@/components/ui/TableBody.vue'
import TableRow from '@/components/ui/TableRow.vue'
import TableHead from '@/components/ui/TableHead.vue'
import TableCell from '@/components/ui/TableCell.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import DocumentUpload from '@/components/documentos/DocumentUpload.vue'
import { formatDate, DOCUMENTO_ESTADO_CONFIG } from '@/lib/utils'

const docStore = useDocumentosStore()
const clientesStore = useClientesStore()
const dealsStore = useDealsStore()

const search = ref('')
const clienteFilter = ref('')
const tipoFilter = ref('')
const estadoFilter = ref('')
const page = ref(1)
const pageSize = 20

const uploadModal = ref(false)
const confirmDeleteId = ref(null)
const deleteLoading = ref(false)

const TIPO_OPTIONS = [
  { value: '', label: 'Todos los tipos' },
  { value: 'contrato', label: 'Contrato' },
  { value: 'propuesta', label: 'Propuesta Comercial' },
  { value: 'nda', label: 'NDA / Confidencialidad' },
  { value: 'factura', label: 'Factura' },
  { value: 'rut', label: 'RUT' },
  { value: 'camara_comercio', label: 'Cámara de Comercio' },
  { value: 'poder', label: 'Poder' },
  { value: 'otro', label: 'Otro' },
]

const ESTADO_OPTIONS = [
  { value: '', label: 'Todos los estados' },
  { value: 'pendiente', label: 'Pendiente' },
  { value: 'recibido', label: 'Recibido' },
  { value: 'aprobado', label: 'Aprobado' },
  { value: 'vencido', label: 'Vencido' },
  { value: 'rechazado', label: 'Rechazado' },
]

const ESTADO_VARIANT = {
  pendiente: 'secondary',
  recibido: 'default',
  aprobado: 'success',
  vencido: 'destructive',
  rechazado: 'destructive',
}

function buildParams() {
  const p = { page: page.value, page_size: pageSize }
  if (search.value) p.search = search.value
  if (clienteFilter.value) p.cliente = clienteFilter.value
  if (tipoFilter.value) p.tipo_documento = tipoFilter.value
  if (estadoFilter.value) p.estado = estadoFilter.value
  return p
}

async function load() { await docStore.fetchDocumentos(buildParams()) }

onMounted(async () => {
  await Promise.all([
    load(),
    clientesStore.fetchClientes({ page_size: 200 }),
    dealsStore.fetchDeals({ page_size: 200 }),
  ])
})

watch([search, clienteFilter, tipoFilter, estadoFilter], () => { page.value = 1; load() })
watch(page, load)

const totalPages = computed(() => Math.ceil(docStore.total / pageSize))

const clienteOptions = computed(() => [
  { value: '', label: 'Todos los clientes' },
  ...clientesStore.clientes.map(c => ({ value: String(c.id), label: c.nombre })),
])

async function doDelete() {
  deleteLoading.value = true
  try { await docStore.deleteDocumento(confirmDeleteId.value); confirmDeleteId.value = null }
  finally { deleteLoading.value = false }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center gap-3">
      <h1 class="text-2xl font-bold flex-1">Documentos</h1>
      <Button @click="uploadModal = true">
        <Plus class="h-4 w-4" />
        Subir Documento
      </Button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-[200px] max-w-xs">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input v-model="search" placeholder="Buscar documentos..." class="pl-9" />
      </div>
      <Select v-model="clienteFilter" :options="clienteOptions" class="w-44" />
      <Select v-model="tipoFilter" :options="TIPO_OPTIONS" class="w-44" />
      <Select v-model="estadoFilter" :options="ESTADO_OPTIONS" class="w-40" />
    </div>

    <!-- Table -->
    <div class="rounded-xl border bg-card shadow-sm overflow-hidden">
      <div v-if="docStore.loading" class="flex justify-center py-16"><Spinner size="lg" /></div>
      <EmptyState
        v-else-if="!docStore.documentos.length"
        :icon="FolderOpen"
        title="Sin documentos"
        description="Sube el primer documento para comenzar."
      />
      <Table v-else>
        <TableHeader>
          <TableRow>
            <TableHead>Nombre</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Cliente</TableHead>
            <TableHead>Deal</TableHead>
            <TableHead>Estado</TableHead>
            <TableHead>Vencimiento</TableHead>
            <TableHead>Subido</TableHead>
            <TableHead class="text-right">Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="doc in docStore.documentos" :key="doc.id">
            <TableCell>
              <div class="flex items-center gap-2">
                <div class="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 flex-shrink-0">
                  <FolderOpen class="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p class="text-sm font-medium truncate max-w-[200px]">{{ doc.nombre }}</p>
                  <p v-if="doc.version" class="text-xs text-muted-foreground">v{{ doc.version }}</p>
                </div>
              </div>
            </TableCell>
            <TableCell class="text-sm text-muted-foreground">{{ doc.tipo_documento_display || doc.tipo_documento || '—' }}</TableCell>
            <TableCell class="text-sm text-muted-foreground">{{ doc.cliente?.nombre || '—' }}</TableCell>
            <TableCell class="text-sm text-muted-foreground">{{ doc.deal?.nombre || '—' }}</TableCell>
            <TableCell>
              <Badge :variant="ESTADO_VARIANT[doc.estado] || 'secondary'">
                {{ DOCUMENTO_ESTADO_CONFIG[doc.estado]?.label || doc.estado || 'Pendiente' }}
              </Badge>
            </TableCell>
            <TableCell>
              <span :class="['text-sm', doc.estado === 'vencido' ? 'text-destructive font-medium' : 'text-muted-foreground']">
                {{ doc.fecha_vencimiento ? formatDate(doc.fecha_vencimiento) : '—' }}
              </span>
            </TableCell>
            <TableCell class="text-xs text-muted-foreground">
              <div>
                <p>{{ doc.subido_por?.first_name || doc.subido_por?.username || '—' }}</p>
                <p>{{ formatDate(doc.created_at) }}</p>
              </div>
            </TableCell>
            <TableCell class="text-right">
              <div class="flex items-center justify-end gap-1">
                <a v-if="doc.archivo" :href="doc.archivo" target="_blank" class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors inline-flex">
                  <Eye class="h-4 w-4" />
                </a>
                <a v-if="doc.archivo" :href="doc.archivo" download class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors inline-flex">
                  <Download class="h-4 w-4" />
                </a>
                <button class="p-1.5 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors" @click="confirmDeleteId = doc.id">
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
      <span>{{ (page-1)*pageSize+1 }}–{{ Math.min(page*pageSize, docStore.total) }} de {{ docStore.total }}</span>
      <div class="flex items-center gap-1">
        <Button variant="outline" size="icon" :disabled="page<=1" @click="page--"><ChevronLeft class="h-4 w-4"/></Button>
        <span class="px-3 text-sm">{{ page }}/{{ totalPages }}</span>
        <Button variant="outline" size="icon" :disabled="page>=totalPages" @click="page++"><ChevronRight class="h-4 w-4"/></Button>
      </div>
    </div>

    <!-- Upload modal -->
    <Dialog :open="uploadModal" size="md" @update:open="uploadModal = $event">
      <DialogHeader>
        <DialogTitle>Subir Documento</DialogTitle>
      </DialogHeader>
      <div class="px-6 pb-6">
        <DocumentUpload @uploaded="uploadModal = false; load()" @cancel="uploadModal = false" />
      </div>
    </Dialog>

    <!-- Confirm delete -->
    <ConfirmDialog
      :open="!!confirmDeleteId"
      title="Eliminar Documento"
      description="El documento se eliminará permanentemente."
      confirm-label="Eliminar"
      :destructive="true"
      :loading="deleteLoading"
      @update:open="confirmDeleteId = null"
      @confirm="doDelete"
      @cancel="confirmDeleteId = null"
    />
  </div>
</template>
