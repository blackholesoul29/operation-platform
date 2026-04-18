<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDealsStore } from '@/stores/deals'
import { Plus, Search, Eye, Edit, Trash2, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
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
import EtapaBadge from '@/components/common/EtapaBadge.vue'
import ServicioBadge from '@/components/common/ServicioBadge.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import { formatCurrency, formatDate, ETAPAS_CONFIG } from '@/lib/utils'
import { Briefcase } from 'lucide-vue-next'

const router = useRouter()
const dealsStore = useDealsStore()

const search = ref('')
const etapaFilter = ref('')
const tipoFilter = ref('')
const estadoFilter = ref('activos')
const page = ref(1)
const pageSize = 15

const confirmDelete = ref(false)
const deletingId = ref(null)
const deleteLoading = ref(false)

const ETAPA_OPTIONS = [
  { value: '', label: 'Todas las etapas' },
  ...Object.entries(ETAPAS_CONFIG).map(([k, v]) => ({ value: k, label: v.label })),
]

const TIPO_OPTIONS = [
  { value: '', label: 'Todos los tipos' },
  { value: 'servicios_principales', label: 'Servicios Principales' },
  { value: 'recs', label: 'RECs' },
]

const ESTADO_OPTIONS = [
  { value: 'activos', label: 'Activos' },
  { value: 'cerrados', label: 'Cerrados' },
  { value: 'todos', label: 'Todos' },
]

function buildParams() {
  const params = { page: page.value, page_size: pageSize }
  if (search.value) params.search = search.value
  if (etapaFilter.value) params.etapa = etapaFilter.value
  if (tipoFilter.value) params.tipo_pipeline = tipoFilter.value
  if (estadoFilter.value === 'activos') params.activo = true
  if (estadoFilter.value === 'cerrados') params.activo = false
  return params
}

async function loadDeals() {
  await dealsStore.fetchDeals(buildParams())
}

onMounted(loadDeals)
watch([search, etapaFilter, tipoFilter, estadoFilter], () => { page.value = 1; loadDeals() })
watch(page, loadDeals)

const totalPages = computed(() => Math.ceil(dealsStore.total / pageSize))

function openDelete(id) {
  deletingId.value = id
  confirmDelete.value = true
}

async function doDelete() {
  deleteLoading.value = true
  try {
    await dealsStore.deleteDeal(deletingId.value)
    confirmDelete.value = false
  } finally {
    deleteLoading.value = false
  }
}

function docsPendientesVariant(count) {
  if (!count) return 'success'
  if (count >= 3) return 'destructive'
  return 'warning'
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex flex-wrap items-center gap-3">
      <h1 class="text-2xl font-bold flex-1">Deals</h1>
      <Button @click="router.push('/deals/nuevo')">
        <Plus class="h-4 w-4" />
        Nuevo Deal
      </Button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3 items-center">
      <div class="relative flex-1 min-w-[200px] max-w-xs">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input v-model="search" placeholder="Buscar deal o cliente..." class="pl-9" />
      </div>
      <Select v-model="etapaFilter" :options="ETAPA_OPTIONS" class="w-44" />
      <Select v-model="tipoFilter" :options="TIPO_OPTIONS" class="w-44" />
      <div class="flex items-center gap-1 bg-muted rounded-lg p-1">
        <button
          v-for="opt in ESTADO_OPTIONS"
          :key="opt.value"
          :class="[
            'rounded-md px-3 py-1 text-xs font-medium transition-all',
            estadoFilter === opt.value
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground',
          ]"
          @click="estadoFilter = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="rounded-xl border bg-card shadow-sm overflow-hidden">
      <div v-if="dealsStore.loading" class="flex justify-center py-16">
        <Spinner size="lg" />
      </div>
      <EmptyState
        v-else-if="!dealsStore.deals.length"
        :icon="Briefcase"
        title="No hay deals"
        description="No se encontraron deals con los filtros aplicados."
      />
      <Table v-else>
        <TableHeader>
          <TableRow>
            <TableHead>Deal</TableHead>
            <TableHead>Cliente</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Etapa</TableHead>
            <TableHead>Comercial</TableHead>
            <TableHead>Valor</TableHead>
            <TableHead class="text-center">Días en etapa</TableHead>
            <TableHead class="text-center">Docs pendientes</TableHead>
            <TableHead class="text-right">Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="deal in dealsStore.deals"
            :key="deal.id"
            class="cursor-pointer"
            @click="router.push(`/deals/${deal.id}`)"
          >
            <TableCell>
              <div>
                <p class="font-medium text-foreground line-clamp-1">{{ deal.nombre }}</p>
                <div class="flex gap-1 mt-1 flex-wrap">
                  <ServicioBadge
                    v-for="svc in (deal.servicios || []).slice(0, 2)"
                    :key="svc"
                    :servicio="svc"
                  />
                  <span
                    v-if="(deal.servicios || []).length > 2"
                    class="text-xs text-muted-foreground"
                  >
                    +{{ deal.servicios.length - 2 }}
                  </span>
                </div>
              </div>
            </TableCell>
            <TableCell>
              <span class="text-sm">{{ deal.cliente?.nombre || '—' }}</span>
            </TableCell>
            <TableCell>
              <Badge variant="secondary" class="text-xs">
                {{ deal.tipo_pipeline === 'recs' ? 'RECs' : 'Servicios' }}
              </Badge>
            </TableCell>
            <TableCell>
              <EtapaBadge :etapa="deal.etapa" />
            </TableCell>
            <TableCell>
              <span class="text-sm text-muted-foreground">
                {{ deal.comercial_asignado?.first_name || deal.comercial_asignado?.username || '—' }}
              </span>
            </TableCell>
            <TableCell>
              <span class="text-sm font-medium">{{ formatCurrency(deal.valor_estimado) }}</span>
            </TableCell>
            <TableCell class="text-center">
              <span class="text-sm text-muted-foreground">{{ deal.dias_en_etapa ?? '—' }}</span>
            </TableCell>
            <TableCell class="text-center">
              <Badge
                v-if="deal.documentos_pendientes > 0"
                :variant="docsPendientesVariant(deal.documentos_pendientes)"
              >
                {{ deal.documentos_pendientes }}
              </Badge>
              <span v-else class="text-xs text-green-600">✓</span>
            </TableCell>
            <TableCell class="text-right" @click.stop>
              <div class="flex items-center justify-end gap-1">
                <button
                  class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                  @click="router.push(`/deals/${deal.id}`)"
                >
                  <Eye class="h-4 w-4" />
                </button>
                <button
                  class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                  @click="router.push(`/deals/${deal.id}/editar`)"
                >
                  <Edit class="h-4 w-4" />
                </button>
                <button
                  class="p-1.5 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                  @click="openDelete(deal.id)"
                >
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
      <span>
        Mostrando {{ (page - 1) * pageSize + 1 }}–{{ Math.min(page * pageSize, dealsStore.total) }}
        de {{ dealsStore.total }} deals
      </span>
      <div class="flex items-center gap-1">
        <Button variant="outline" size="icon" :disabled="page <= 1" @click="page--">
          <ChevronLeft class="h-4 w-4" />
        </Button>
        <span class="px-3 py-1 text-sm font-medium">{{ page }} / {{ totalPages }}</span>
        <Button variant="outline" size="icon" :disabled="page >= totalPages" @click="page++">
          <ChevronRight class="h-4 w-4" />
        </Button>
      </div>
    </div>

    <!-- Confirm Delete -->
    <ConfirmDialog
      :open="confirmDelete"
      title="Eliminar Deal"
      description="Esta acción eliminará permanentemente el deal y todos sus datos asociados."
      confirm-label="Eliminar"
      :destructive="true"
      :loading="deleteLoading"
      @update:open="confirmDelete = $event"
      @confirm="doDelete"
      @cancel="confirmDelete = false"
    />
  </div>
</template>
