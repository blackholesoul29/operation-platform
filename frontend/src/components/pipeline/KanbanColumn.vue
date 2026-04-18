<script setup>
import { ref, computed } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { Plus } from 'lucide-vue-next'
import DealCard from './DealCard.vue'
import { ETAPAS_CONFIG } from '@/lib/utils'

const props = defineProps({
  etapa: { type: String, required: true },
  deals: { type: Array, default: () => [] },
})

const emit = defineEmits(['deal-moved', 'add-deal'])

const config = computed(() => ETAPAS_CONFIG[props.etapa] || { label: props.etapa, color: '', dotColor: '' })

const localDeals = ref([...props.deals])

// Keep localDeals in sync with prop
import { watch } from 'vue'
watch(
  () => props.deals,
  (val) => { localDeals.value = [...val] },
  { deep: true }
)

function onEnd(event) {
  // If the item was moved from another list into this one
  if (event.from !== event.to) {
    const dealId = parseInt(event.item.dataset.dealId)
    emit('deal-moved', dealId, props.etapa)
  }
}

const totalValor = computed(() =>
  props.deals.reduce((acc, d) => acc + (parseFloat(d.valor_estimado) || 0), 0)
)
</script>

<template>
  <div class="flex-shrink-0 w-72 flex flex-col bg-slate-50 rounded-xl border border-slate-200 max-h-full">
    <!-- Column header -->
    <div
      :class="['flex items-center justify-between px-3 py-3 rounded-t-xl border-b', config.headerColor || 'bg-slate-50 border-slate-200']"
    >
      <div class="flex items-center gap-2 min-w-0">
        <span :class="['h-2.5 w-2.5 rounded-full flex-shrink-0', config.dotColor]" />
        <span class="text-sm font-semibold text-slate-700 truncate">{{ config.label }}</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs text-slate-500 font-medium bg-white rounded-full px-2 py-0.5 border">
          {{ deals.length }}
        </span>
      </div>
    </div>

    <!-- Cards list -->
    <VueDraggable
      v-model="localDeals"
      :group="{ name: 'pipeline', pull: true, put: true }"
      item-key="id"
      ghost-class="sortable-ghost"
      drag-class="sortable-drag"
      class="flex-1 overflow-y-auto p-2 space-y-2 min-h-[80px]"
      @end="onEnd"
    >
      <template #item="{ element }">
        <DealCard
          :deal="element"
          :data-deal-id="element.id"
        />
      </template>
    </VueDraggable>

    <!-- Add button -->
    <div class="p-2 border-t border-slate-200">
      <button
        class="flex w-full items-center justify-center gap-1.5 rounded-lg py-2 text-xs font-medium text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
        @click="emit('add-deal', etapa)"
      >
        <Plus class="h-3.5 w-3.5" />
        Agregar deal
      </button>
    </div>
  </div>
</template>
