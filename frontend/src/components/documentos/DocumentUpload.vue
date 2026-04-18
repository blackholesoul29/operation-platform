<script setup>
import { ref, reactive } from 'vue'
import { UploadCloud, File, X, CheckCircle } from 'lucide-vue-next'
import { useDocumentosStore } from '@/stores/documentos'
import { formatFileSize } from '@/lib/utils'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import Spinner from '@/components/ui/Spinner.vue'

const props = defineProps({
  dealId: { type: [Number, String], default: null },
  clienteId: { type: [Number, String], default: null },
})

const emit = defineEmits(['uploaded', 'cancel'])

const docStore = useDocumentosStore()
const isDragging = ref(false)
const selectedFile = ref(null)
const loading = ref(false)
const error = ref('')
const success = ref(false)

const form = reactive({
  nombre: '',
  tipo_documento: '',
  descripcion: '',
  fecha_vencimiento: '',
})

const TIPO_OPTIONS = [
  { value: 'contrato', label: 'Contrato' },
  { value: 'propuesta', label: 'Propuesta Comercial' },
  { value: 'nda', label: 'NDA / Confidencialidad' },
  { value: 'factura', label: 'Factura' },
  { value: 'rut', label: 'RUT' },
  { value: 'camara_comercio', label: 'Cámara de Comercio' },
  { value: 'poder', label: 'Poder' },
  { value: 'otro', label: 'Otro' },
]

function onDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) setFile(file)
}

function onFileInput(e) {
  const file = e.target.files[0]
  if (file) setFile(file)
}

function setFile(file) {
  selectedFile.value = file
  if (!form.nombre) form.nombre = file.name.replace(/\.[^/.]+$/, '')
}

function removeFile() {
  selectedFile.value = null
}

async function upload() {
  if (!selectedFile.value) { error.value = 'Selecciona un archivo'; return }
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }

  loading.value = true
  error.value = ''

  const fd = new FormData()
  fd.append('archivo', selectedFile.value)
  fd.append('nombre', form.nombre)
  if (form.tipo_documento) fd.append('tipo_documento', form.tipo_documento)
  if (form.descripcion) fd.append('descripcion', form.descripcion)
  if (form.fecha_vencimiento) fd.append('fecha_vencimiento', form.fecha_vencimiento)
  if (props.dealId) fd.append('deal', props.dealId)
  if (props.clienteId) fd.append('cliente', props.clienteId)

  try {
    const data = await docStore.uploadDocumento(fd)
    success.value = true
    emit('uploaded', data)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al subir el documento'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div v-if="error" class="rounded-md bg-destructive/10 px-4 py-2 text-sm text-destructive">
      {{ error }}
    </div>

    <!-- Drop zone -->
    <div
      v-if="!selectedFile"
      :class="[
        'flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-colors cursor-pointer',
        isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-muted/30',
      ]"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="onDrop"
      @click="$refs.fileInput.click()"
    >
      <UploadCloud class="h-10 w-10 text-muted-foreground mb-3" />
      <p class="text-sm font-medium text-foreground">Arrastra o haz clic para subir</p>
      <p class="text-xs text-muted-foreground mt-1">PDF, Word, Excel, imágenes hasta 50MB</p>
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg"
        @change="onFileInput"
      />
    </div>

    <!-- File preview -->
    <div
      v-else
      class="flex items-center gap-3 rounded-lg border bg-muted/30 px-4 py-3"
    >
      <div class="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10">
        <File class="h-5 w-5 text-primary" />
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium truncate">{{ selectedFile.name }}</p>
        <p class="text-xs text-muted-foreground">{{ formatFileSize(selectedFile.size) }}</p>
      </div>
      <button class="text-muted-foreground hover:text-destructive transition-colors" @click="removeFile">
        <X class="h-4 w-4" />
      </button>
    </div>

    <!-- Form fields -->
    <div class="space-y-3">
      <div class="space-y-1.5">
        <Label>Nombre del documento *</Label>
        <Input v-model="form.nombre" placeholder="Ej: Contrato Marco 2024" />
      </div>

      <div class="space-y-1.5">
        <Label>Tipo de documento</Label>
        <Select v-model="form.tipo_documento" :options="TIPO_OPTIONS" placeholder="Seleccionar tipo..." />
      </div>

      <div class="space-y-1.5">
        <Label>Descripción</Label>
        <Input v-model="form.descripcion" placeholder="Descripción opcional..." />
      </div>

      <div class="space-y-1.5">
        <Label>Fecha de vencimiento</Label>
        <Input v-model="form.fecha_vencimiento" type="date" />
      </div>
    </div>

    <div class="flex gap-3 pt-2">
      <Button variant="outline" class="flex-1" @click="emit('cancel')">Cancelar</Button>
      <Button class="flex-1" :disabled="loading || !selectedFile" @click="upload">
        <Spinner v-if="loading" size="sm" class="mr-2" />
        Subir Documento
      </Button>
    </div>
  </div>
</template>
