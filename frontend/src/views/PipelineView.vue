<script setup>
import { onMounted, ref, reactive, computed } from 'vue'
import { useDealsStore } from '@/stores/deals'
import { useClientesStore } from '@/stores/clientes'
import { Plus, Filter } from 'lucide-vue-next'
import KanbanBoard from '@/components/pipeline/KanbanBoard.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Button from '@/components/ui/Button.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import Spinner from '@/components/ui/Spinner.vue'
import DealFormModal from '@/components/deals/DealFormModal.vue'
import EtapaBadge from '@/components/common/EtapaBadge.vue'
import { ETAPAS_CONFIG, ETAPAS_ORDER } from '@/lib/utils'

const dealsStore = useDealsStore()
const clientesStore = useClientesStore()

const moveModal = ref(false)
const createModal = ref(false)
const loadingMove = ref(false)
const selectedEtapaCreate = ref('prospeccion')

const pendingMove = reactive({
  dealId: null,
  dealNombre: '',
  fromEtapa: '',
  toEtapa: '',
  motivo: '',
})

const filtroActivo = ref('all')
const filtros = [
  { key: 'all', label: 'Todos' },
  { key: 'servicios_principales', label: 'Servicios Principales' },
  { key: 'recs', label: 'RECs' },
]

onMounted(() => {
  dealsStore.fetchPipeline()
})

const pipelineFiltered = computed(() => {
  if (filtroActivo.value === 'all') return dealsStore.pipeline
  const result = {}
  for (const [etapa, deals] of Object.entries(dealsStore.pipeline)) {
    result[etapa] = (deals || []).filter((d) => d.tipo_pipeline === filtroActivo.value)
  }
  return result
})

function onDealMoved(dealId, newEtapa) {
  // Find deal in pipeline
  let deal = null
  let fromEtapa = ''
  for (const [etapa, deals] of Object.entries(dealsStore.pipeline)) {
    const found = (deals || []).find((d) => d.id === dealId)
    if (found) { deal = found; fromEtapa = etapa; break }
  }

  if (!deal || fromEtapa === newEtapa) return

  pendingMove.dealId = dealId
  pendingMove.dealNombre = deal.nombre
  pendingMove.fromEtapa = fromEtapa
  pendingMove.toEtapa = newEtapa
  pendingMove.motivo = ''
  moveModal.value = true
}

async function confirmMove() {
  loadingMove.value = true
  try {
    await dealsStore.cambiarEtapa(pendingMove.dealId, {
      etapa: pendingMove.toEtapa,
      motivo: pendingMove.motivo,
    })
    await dealsStore.fetchPipeline()
    moveModal.value = false
  } catch {
    //
  } finally {
    loadingMove.value = false
  }
}

function cancelMove() {
  moveModal.value = false
  dealsStore.fetchPipeline()
}

function onAddDeal(etapa) {
  selectedEtapaCreate.value = etapa
  createModal.value = true
}

function onDealCreated() {
  dealsStore.fetchPipeline()
  createModal.value = false
}
</script>

<template>
  <div class="flex flex-col h-full -m-6 p-6 overflow-hidden">
    <!-- Header -->
    <div class="flex flex-wrap items-center gap-3 mb-4 flex-shrink-0">
      <!-- Filters -->
      <div class="flex items-center gap-1 bg-muted rounded-lg p-1">
        <button
          v-for="f in filtros"
          :key="f.key"
          :class="[
            'rounded-md px-3 py-1.5 text-sm font-medium transition-all',
            filtroActivo === f.key
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground',
          ]"
          @click="filtroActivo = f.key"
        >
          {{ f.label }}
        </button>
      </div>

      <div class="ml-auto">
        <Button @click="createModal = true">
          <Plus class="h-4 w-4 mr-1" />
          Nuevo Deal
        </Button>
      </div>
    </div>

    <!-- Kanban -->
    <div class="flex-1 overflow-hidden">
      <div v-if="dealsStore.loading" class="flex h-full items-center justify-center">
        <Spinner size="lg" />
      </div>
      <KanbanBoard
        v-else
        :pipeline="pipelineFiltered"
        @deal-moved="onDealMoved"
        @add-deal="onAddDeal"
      />
    </div>

    <!-- Move confirmation modal -->
    <Dialog :open="moveModal" size="sm" @update:open="cancelMove">
      <DialogHeader>
        <DialogTitle>Cambiar Etapa</DialogTitle>
      </DialogHeader>
      <div class="px-6 pb-4 space-y-4">
        <p class="text-sm text-muted-foreground">
          Mover <span class="font-semibold text-foreground">{{ pendingMove.dealNombre }}</span>
        </p>
        <div class="flex items-center gap-3">
          <EtapaBadge :etapa="pendingMove.fromEtapa" />
          <span class="text-muted-foreground">→</span>
          <EtapaBadge :etapa="pendingMove.toEtapa" />
        </div>
        <div class="space-y-1.5">
          <Label>Motivo del cambio (opcional)</Label>
          <Textarea
            v-model="pendingMove.motivo"
            placeholder="Describe el motivo del cambio de etapa..."
            class="min-h-[80px]"
          />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" :disabled="loadingMove" @click="cancelMove">Cancelar</Button>
        <Button :disabled="loadingMove" @click="confirmMove">
          <Spinner v-if="loadingMove" size="sm" class="mr-2" />
          Confirmar
        </Button>
      </DialogFooter>
    </Dialog>

    <!-- Create deal modal -->
    <DealFormModal
      :open="createModal"
      :etapa-inicial="selectedEtapaCreate"
      @update:open="createModal = $event"
      @created="onDealCreated"
    />
  </div>
</template>
