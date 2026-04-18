<script setup>
import { onMounted, ref, computed, reactive } from 'vue'
import { Plus, Edit, Trash2, Users, Shield, Eye, EyeOff } from 'lucide-vue-next'
import api from '@/lib/api'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
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
import DialogFooter from '@/components/ui/DialogFooter.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import Avatar from '@/components/ui/Avatar.vue'
import { getInitials, ROLES_CONFIG } from '@/lib/utils'

const users = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingId = ref(null)
const saving = ref(false)
const formError = ref('')
const showPassword = ref(false)
const confirmDeleteId = ref(null)
const deleteLoading = ref(false)

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'comercial',
  password: '',
  is_active: true,
})

const ROLE_OPTIONS = [
  { value: 'admin', label: 'Administrador' },
  { value: 'manager_comercial', label: 'Manager Comercial' },
  { value: 'comercial', label: 'Comercial' },
  { value: 'operaciones', label: 'Operaciones' },
  { value: 'viewer', label: 'Visualizador' },
]

async function loadUsers() {
  loading.value = true
  try {
    const { data } = await api.get('/users/')
    users.value = data.results || data
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)

function openCreate() {
  editingId.value = null
  Object.assign(form, { username: '', email: '', first_name: '', last_name: '', role: 'comercial', password: '', is_active: true })
  formError.value = ''
  showModal.value = true
}

function openEdit(user) {
  editingId.value = user.id
  Object.assign(form, {
    username: user.username || '',
    email: user.email || '',
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    role: user.role || 'comercial',
    password: '',
    is_active: user.is_active !== false,
  })
  formError.value = ''
  showModal.value = true
}

async function saveUser() {
  if (!form.username.trim()) { formError.value = 'El username es requerido'; return }
  if (!editingId.value && !form.password) { formError.value = 'La contraseña es requerida para nuevos usuarios'; return }

  saving.value = true
  formError.value = ''

  const payload = { ...form }
  if (!payload.password) delete payload.password

  try {
    if (editingId.value) {
      await api.patch(`/users/${editingId.value}/`, payload)
    } else {
      await api.post('/users/', payload)
    }
    showModal.value = false
    loadUsers()
  } catch (e) {
    const d = e.response?.data
    formError.value = typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Error al guardar'
  } finally {
    saving.value = false
  }
}

async function deleteUser() {
  deleteLoading.value = true
  try {
    await api.delete(`/users/${confirmDeleteId.value}/`)
    users.value = users.value.filter(u => u.id !== confirmDeleteId.value)
    confirmDeleteId.value = null
  } finally {
    deleteLoading.value = false
  }
}

function roleLabel(role) {
  return ROLES_CONFIG[role]?.label || role
}

function roleVariant(role) {
  const map = { admin: 'destructive', manager_comercial: 'default', comercial: 'secondary', operaciones: 'success', viewer: 'outline' }
  return map[role] || 'secondary'
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center gap-3">
      <h1 class="text-2xl font-bold flex-1">Gestión de Usuarios</h1>
      <Button @click="openCreate">
        <Plus class="h-4 w-4" />
        Nuevo Usuario
      </Button>
    </div>

    <div class="rounded-xl border bg-card shadow-sm overflow-hidden">
      <div v-if="loading" class="flex justify-center py-16"><Spinner size="lg" /></div>
      <EmptyState v-else-if="!users.length" :icon="Users" title="Sin usuarios" description="Crea el primer usuario del sistema." />
      <Table v-else>
        <TableHeader>
          <TableRow>
            <TableHead>Usuario</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Rol</TableHead>
            <TableHead>Estado</TableHead>
            <TableHead class="text-right">Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="u in users" :key="u.id">
            <TableCell>
              <div class="flex items-center gap-2.5">
                <Avatar :fallback="getInitials(`${u.first_name || ''} ${u.last_name || ''}`) || u.username?.slice(0,2).toUpperCase()" size="sm" />
                <div>
                  <p class="text-sm font-medium">
                    {{ u.first_name ? `${u.first_name} ${u.last_name || ''}`.trim() : u.username }}
                  </p>
                  <p class="text-xs text-muted-foreground">@{{ u.username }}</p>
                </div>
              </div>
            </TableCell>
            <TableCell class="text-sm text-muted-foreground">{{ u.email || '—' }}</TableCell>
            <TableCell>
              <Badge :variant="roleVariant(u.role)">{{ roleLabel(u.role) }}</Badge>
            </TableCell>
            <TableCell>
              <Badge :variant="u.is_active !== false ? 'success' : 'secondary'">
                {{ u.is_active !== false ? 'Activo' : 'Inactivo' }}
              </Badge>
            </TableCell>
            <TableCell class="text-right">
              <div class="flex items-center justify-end gap-1">
                <button class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors" @click="openEdit(u)">
                  <Edit class="h-4 w-4" />
                </button>
                <button class="p-1.5 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors" @click="confirmDeleteId = u.id">
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Create/Edit modal -->
    <Dialog :open="showModal" size="md" @update:open="showModal = $event">
      <DialogHeader>
        <DialogTitle>{{ editingId ? 'Editar Usuario' : 'Nuevo Usuario' }}</DialogTitle>
      </DialogHeader>
      <div class="px-6 pb-4 space-y-4">
        <div v-if="formError" class="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{{ formError }}</div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <Label>Nombre *</Label>
            <Input v-model="form.first_name" placeholder="Juan" />
          </div>
          <div class="space-y-1.5">
            <Label>Apellido</Label>
            <Input v-model="form.last_name" placeholder="Pérez" />
          </div>
          <div class="space-y-1.5">
            <Label>Username *</Label>
            <Input v-model="form.username" placeholder="juan.perez" />
          </div>
          <div class="space-y-1.5">
            <Label>Email</Label>
            <Input v-model="form.email" type="email" placeholder="juan@empresa.com" />
          </div>
          <div class="space-y-1.5">
            <Label>Rol</Label>
            <Select v-model="form.role" :options="ROLE_OPTIONS" />
          </div>
          <div class="space-y-1.5">
            <Label>{{ editingId ? 'Nueva Contraseña' : 'Contraseña *' }}</Label>
            <div class="relative">
              <Input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                class="pr-10"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                @click="showPassword = !showPassword"
              >
                <Eye v-if="!showPassword" class="h-4 w-4" />
                <EyeOff v-else class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        <label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" v-model="form.is_active" class="h-4 w-4 accent-primary rounded" />
          <span class="text-sm">Usuario activo</span>
        </label>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="showModal = false">Cancelar</Button>
        <Button :disabled="saving" @click="saveUser">
          <Spinner v-if="saving" size="sm" class="mr-2" />
          {{ editingId ? 'Guardar Cambios' : 'Crear Usuario' }}
        </Button>
      </DialogFooter>
    </Dialog>

    <!-- Confirm delete -->
    <ConfirmDialog
      :open="!!confirmDeleteId"
      title="Eliminar Usuario"
      description="El usuario será eliminado permanentemente del sistema."
      confirm-label="Eliminar"
      :destructive="true"
      :loading="deleteLoading"
      @update:open="confirmDeleteId = null"
      @confirm="deleteUser"
      @cancel="confirmDeleteId = null"
    />
  </div>
</template>
