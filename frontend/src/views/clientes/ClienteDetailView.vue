<script setup>
import { onMounted, ref, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClientesStore } from '@/stores/clientes'
import { useDocumentosStore } from '@/stores/documentos'
import { useTareasStore } from '@/stores/tareas'
import {
  ArrowLeft, Edit, Plus, Trash2, Mail, Phone, Globe, MapPin, Building2, User
} from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Badge from '@/components/ui/Badge.vue'
import Spinner from '@/components/ui/Spinner.vue'
import Separator from '@/components/ui/Separator.vue'
import Avatar from '@/components/ui/Avatar.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import EtapaBadge from '@/components/common/EtapaBadge.vue'
import ServicioBadge from '@/components/common/ServicioBadge.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import DocumentUpload from '@/components/documentos/DocumentUpload.vue'
import { formatCurrency, formatDate, getInitials, DOCUMENTO_ESTADO_CONFIG } from '@/lib/utils'

const route = useRoute()
const router = useRouter()
const clientesStore = useClientesStore()
const docStore = useDocumentosStore()
const tareasStore = useTareasStore()

const activeTab = ref('info')
const loading = ref(true)
const cliente = computed(() => clientesStore.currentCliente)

const contactModal = ref(false)
const editingContactId = ref(null)
const contactForm = reactive({ nombre: '', cargo: '', email: '', telefono: '', principal: false })
const savingContact = ref(false)

const uploadDocModal = ref(false)
const confirmDeleteContactId = ref(null)

const tabs = [
  { key: 'info', label: 'Información' },
  { key: 'deals', label: 'Deals' },
  { key: 'documentos', label: 'Documentos' },
  { key: 'tareas', label: 'Tareas' },
]

onMounted(async () => {
  loading.value = true
  try {
    await clientesStore.fetchCliente(route.params.id)
    await Promise.all([
      docStore.fetchDocumentos({ cliente: route.params.id }),
      tareasStore.fetchTareas({ cliente: route.params.id }),
    ])
  } finally {
    loading.value = false
  }
})

function openAddContact() {
  editingContactId.value = null
  Object.assign(contactForm, { nombre: '', cargo: '', email: '', telefono: '', principal: false })
  contactModal.value = true
}

function openEditContact(c) {
  editingContactId.value = c.id
  Object.assign(contactForm, { nombre: c.nombre || '', cargo: c.cargo || '', email: c.email || '', telefono: c.telefono || '', principal: c.principal || false })
  contactModal.value = true
}

async function saveContact() {
  if (!contactForm.nombre.trim()) return
  savingContact.value = true
  try {
    if (editingContactId.value) {
      await clientesStore.updateContacto(cliente.value.id, editingContactId.value, { ...contactForm })
    } else {
      await clientesStore.addContacto(cliente.value.id, { ...contactForm })
    }
    contactModal.value = false
  } finally {
    savingContact.value = false
  }
}

async function deleteContact(contactId) {
  await clientesStore.deleteContacto(cliente.value.id, contactId)
  confirmDeleteContactId.value = null
}

const dealsActivos = computed(() => (cliente.value?.deals || []).filter(d => !['cerrado_ganado','cerrado_perdido','sin_interes'].includes(d.etapa)))
const dealsCerrados = computed(() => (cliente.value?.deals || []).filter(d => ['cerrado_ganado','cerrado_perdido','sin_interes'].includes(d.etapa)))

const SEGMENTO_MAP = {
  gran_consumidor: 'Gran Consumidor',
  generador: 'Generador',
  comercializador: 'Comercializador',
  autogenerador: 'Autogenerador',
  otro: 'Otro',
}

const ESTADO_BADGE = {
  pendiente: 'secondary',
  recibido: 'default',
  aprobado: 'success',
  vencido: 'destructive',
  rechazado: 'destructive',
}
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-20">
      <Spinner size="xl" />
    </div>
    <div v-else-if="!cliente" class="text-center py-20 text-muted-foreground">
      Cliente no encontrado.
    </div>

    <template v-else>
      <!-- Header -->
      <div class="flex flex-wrap items-center gap-3 mb-6">
        <button class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground" @click="router.push('/clientes')">
          <ArrowLeft class="h-4 w-4" /> Clientes
        </button>
        <Separator orientation="vertical" class="h-4" />
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-sm font-bold text-primary flex-shrink-0">
            {{ cliente.nombre?.slice(0, 2).toUpperCase() }}
          </div>
          <div class="min-w-0">
            <h1 class="text-xl font-bold truncate">{{ cliente.nombre }}</h1>
            <p v-if="cliente.nit" class="text-sm text-muted-foreground">NIT: {{ cliente.nit }}</p>
          </div>
        </div>
        <Badge v-if="cliente.segmento" variant="secondary">{{ SEGMENTO_MAP[cliente.segmento] || cliente.segmento }}</Badge>
      </div>

      <!-- Tabs -->
      <div class="flex border-b mb-6 gap-1">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="[
            'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors',
            activeTab === tab.key
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground',
          ]"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab: Información -->
      <div v-if="activeTab === 'info'" class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <!-- Main info -->
        <Card class="lg:col-span-2">
          <CardHeader class="pb-3">
            <CardTitle class="text-sm">Datos de la Empresa</CardTitle>
          </CardHeader>
          <CardContent class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-muted-foreground mb-0.5">Nombre</p>
              <p class="text-sm font-medium">{{ cliente.nombre }}</p>
            </div>
            <div>
              <p class="text-xs text-muted-foreground mb-0.5">NIT</p>
              <p class="text-sm font-medium">{{ cliente.nit || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-muted-foreground mb-0.5">Segmento</p>
              <p class="text-sm">{{ SEGMENTO_MAP[cliente.segmento] || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-muted-foreground mb-0.5">Ciudad</p>
              <p class="text-sm">{{ cliente.ciudad || '—' }}</p>
            </div>
            <div v-if="cliente.telefono" class="flex items-center gap-1.5">
              <Phone class="h-3.5 w-3.5 text-muted-foreground" />
              <p class="text-sm">{{ cliente.telefono }}</p>
            </div>
            <div v-if="cliente.email_contacto" class="flex items-center gap-1.5">
              <Mail class="h-3.5 w-3.5 text-muted-foreground" />
              <p class="text-sm">{{ cliente.email_contacto }}</p>
            </div>
            <div v-if="cliente.website" class="flex items-center gap-1.5">
              <Globe class="h-3.5 w-3.5 text-muted-foreground" />
              <a :href="cliente.website" target="_blank" class="text-sm text-primary hover:underline">{{ cliente.website }}</a>
            </div>
            <div v-if="cliente.direccion" class="flex items-center gap-1.5 col-span-2">
              <MapPin class="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
              <p class="text-sm">{{ cliente.direccion }}</p>
            </div>
            <div v-if="cliente.comercial_asignado" class="col-span-2">
              <p class="text-xs text-muted-foreground mb-1">Comercial Asignado</p>
              <div class="flex items-center gap-2">
                <Avatar :fallback="getInitials(`${cliente.comercial_asignado.first_name || ''} ${cliente.comercial_asignado.last_name || ''}`) || '?'" size="sm" />
                <p class="text-sm font-medium">{{ cliente.comercial_asignado.first_name || cliente.comercial_asignado.username }}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Stats -->
        <div class="space-y-4">
          <Card>
            <CardContent class="p-5 grid grid-cols-2 gap-4">
              <div class="text-center">
                <p class="text-2xl font-bold text-primary">{{ cliente.deals_activos ?? 0 }}</p>
                <p class="text-xs text-muted-foreground mt-0.5">Deals Activos</p>
              </div>
              <div class="text-center">
                <p class="text-2xl font-bold text-green-600">{{ cliente.deals_cerrados ?? 0 }}</p>
                <p class="text-xs text-muted-foreground mt-0.5">Cerrados</p>
              </div>
            </CardContent>
          </Card>

          <!-- Contacts -->
          <Card>
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-sm">Contactos</CardTitle>
                <Button size="sm" variant="outline" @click="openAddContact">
                  <Plus class="h-3.5 w-3.5" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div v-if="!cliente.contactos?.length" class="text-center py-4 text-xs text-muted-foreground">Sin contactos</div>
              <ul v-else class="space-y-3">
                <li v-for="ct in cliente.contactos" :key="ct.id" class="flex items-start gap-2.5">
                  <Avatar :fallback="getInitials(ct.nombre)" size="sm" />
                  <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-1">
                      <p class="text-sm font-medium truncate">{{ ct.nombre }}</p>
                      <Badge v-if="ct.principal" variant="success" class="text-[10px] py-0 px-1.5">Principal</Badge>
                    </div>
                    <p class="text-xs text-muted-foreground">{{ ct.cargo || '' }}</p>
                    <p v-if="ct.email" class="text-xs text-muted-foreground truncate">{{ ct.email }}</p>
                  </div>
                  <div class="flex gap-1 flex-shrink-0">
                    <button class="p-1 text-muted-foreground hover:text-foreground transition-colors" @click="openEditContact(ct)">
                      <Edit class="h-3.5 w-3.5" />
                    </button>
                    <button class="p-1 text-muted-foreground hover:text-destructive transition-colors" @click="confirmDeleteContactId = ct.id">
                      <Trash2 class="h-3.5 w-3.5" />
                    </button>
                  </div>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      <!-- Tab: Deals -->
      <div v-if="activeTab === 'deals'" class="space-y-5">
        <div v-if="dealsActivos.length">
          <h3 class="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wide">Activos ({{ dealsActivos.length }})</h3>
          <div class="space-y-2">
            <div
              v-for="deal in dealsActivos"
              :key="deal.id"
              class="flex items-center gap-4 rounded-xl border bg-card p-4 cursor-pointer hover:border-primary/30 hover:shadow-sm transition-all"
              @click="router.push(`/deals/${deal.id}`)"
            >
              <div class="flex-1 min-w-0">
                <p class="font-medium truncate">{{ deal.nombre }}</p>
                <div class="flex flex-wrap gap-1 mt-1">
                  <ServicioBadge v-for="svc in (deal.servicios || []).slice(0, 3)" :key="svc" :servicio="svc" />
                </div>
              </div>
              <EtapaBadge :etapa="deal.etapa" class="flex-shrink-0" />
              <p class="text-sm font-semibold text-muted-foreground flex-shrink-0">{{ formatCurrency(deal.valor_estimado) }}</p>
            </div>
          </div>
        </div>

        <div v-if="dealsCerrados.length">
          <h3 class="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wide">Cerrados ({{ dealsCerrados.length }})</h3>
          <div class="space-y-2">
            <div
              v-for="deal in dealsCerrados"
              :key="deal.id"
              class="flex items-center gap-4 rounded-xl border bg-card p-4 cursor-pointer hover:border-primary/30 transition-all opacity-70"
              @click="router.push(`/deals/${deal.id}`)"
            >
              <div class="flex-1 min-w-0">
                <p class="font-medium truncate">{{ deal.nombre }}</p>
              </div>
              <EtapaBadge :etapa="deal.etapa" class="flex-shrink-0" />
              <p class="text-sm font-semibold text-muted-foreground flex-shrink-0">{{ formatCurrency(deal.valor_estimado) }}</p>
            </div>
          </div>
        </div>

        <div v-if="!cliente.deals?.length" class="text-center py-12 text-muted-foreground">
          <Building2 class="h-12 w-12 mx-auto mb-3 opacity-30" />
          <p>Sin deals para este cliente</p>
          <Button class="mt-4" @click="router.push('/deals/nuevo')">Crear primer deal</Button>
        </div>
      </div>

      <!-- Tab: Documentos -->
      <div v-if="activeTab === 'documentos'" class="space-y-4">
        <div class="flex justify-between items-center">
          <p class="text-sm text-muted-foreground">{{ docStore.documentos.length }} documento(s)</p>
          <Button size="sm" @click="uploadDocModal = true">
            <Plus class="h-4 w-4 mr-1" />Subir Documento
          </Button>
        </div>
        <div v-if="docStore.loading" class="flex justify-center py-10"><Spinner /></div>
        <div v-else-if="!docStore.documentos.length" class="text-center py-12 text-muted-foreground">Sin documentos</div>
        <div v-else class="space-y-2">
          <div
            v-for="doc in docStore.documentos"
            :key="doc.id"
            class="flex items-center gap-3 rounded-xl border bg-card p-4"
          >
            <div class="flex-1 min-w-0">
              <p class="font-medium truncate">{{ doc.nombre }}</p>
              <p class="text-xs text-muted-foreground">{{ doc.tipo_documento_display || doc.tipo_documento }} · {{ formatDate(doc.created_at) }}</p>
            </div>
            <Badge :variant="ESTADO_BADGE[doc.estado] || 'secondary'">{{ DOCUMENTO_ESTADO_CONFIG[doc.estado]?.label || doc.estado }}</Badge>
            <a v-if="doc.archivo" :href="doc.archivo" target="_blank" class="text-sm text-primary hover:underline">Ver</a>
          </div>
        </div>
      </div>

      <!-- Tab: Tareas -->
      <div v-if="activeTab === 'tareas'" class="space-y-3">
        <div v-if="tareasStore.loading" class="flex justify-center py-10"><Spinner /></div>
        <div v-else-if="!tareasStore.tareas.length" class="text-center py-12 text-muted-foreground">Sin tareas</div>
        <div v-else class="space-y-2">
          <div
            v-for="t in tareasStore.tareas"
            :key="t.id"
            class="flex items-center gap-3 rounded-xl border bg-card p-4"
          >
            <div :class="['h-5 w-5 rounded-full border-2 flex items-center justify-center flex-shrink-0', t.completada ? 'border-green-500 bg-green-500' : 'border-border']">
              <svg v-if="t.completada" class="h-3 w-3 text-white" viewBox="0 0 12 12" fill="none">
                <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p :class="['text-sm font-medium truncate', t.completada ? 'line-through text-muted-foreground' : '']">{{ t.titulo }}</p>
              <p v-if="t.fecha_limite" class="text-xs text-muted-foreground">Vence: {{ formatDate(t.fecha_limite) }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Contact modal -->
    <Dialog :open="contactModal" size="sm" @update:open="contactModal = $event">
      <DialogHeader>
        <DialogTitle>{{ editingContactId ? 'Editar Contacto' : 'Nuevo Contacto' }}</DialogTitle>
      </DialogHeader>
      <div class="px-6 pb-4 space-y-3">
        <div class="space-y-1.5">
          <Label>Nombre *</Label>
          <Input v-model="contactForm.nombre" placeholder="Nombre completo" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-1.5">
            <Label>Cargo</Label>
            <Input v-model="contactForm.cargo" placeholder="Gerente Energía" />
          </div>
          <div class="space-y-1.5">
            <Label>Teléfono</Label>
            <Input v-model="contactForm.telefono" placeholder="+57..." />
          </div>
        </div>
        <div class="space-y-1.5">
          <Label>Email</Label>
          <Input v-model="contactForm.email" type="email" placeholder="contacto@empresa.com" />
        </div>
        <label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" v-model="contactForm.principal" class="h-4 w-4 accent-primary rounded" />
          <span class="text-sm">Contacto principal</span>
        </label>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="contactModal = false">Cancelar</Button>
        <Button :disabled="savingContact" @click="saveContact">
          <Spinner v-if="savingContact" size="sm" class="mr-2" />
          Guardar
        </Button>
      </DialogFooter>
    </Dialog>

    <!-- Delete contact confirm -->
    <ConfirmDialog
      :open="!!confirmDeleteContactId"
      title="Eliminar Contacto"
      description="¿Eliminar este contacto?"
      confirm-label="Eliminar"
      :destructive="true"
      @update:open="confirmDeleteContactId = null"
      @confirm="deleteContact(confirmDeleteContactId)"
      @cancel="confirmDeleteContactId = null"
    />

    <!-- Upload doc modal -->
    <Dialog :open="uploadDocModal" size="md" @update:open="uploadDocModal = $event">
      <DialogHeader>
        <DialogTitle>Subir Documento</DialogTitle>
      </DialogHeader>
      <div class="px-6 pb-6">
        <DocumentUpload
          :cliente-id="cliente?.id"
          @uploaded="uploadDocModal = false; docStore.fetchDocumentos({ cliente: route.params.id })"
          @cancel="uploadDocModal = false"
        />
      </div>
    </Dialog>
  </div>
</template>
