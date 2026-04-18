<script setup>
import KanbanColumn from './KanbanColumn.vue'

const ETAPAS_ACTIVAS = [
  'prospeccion',
  'primer_contacto',
  'oferta_enviada',
  'negociacion',
  'contrato',
]

const props = defineProps({
  pipeline: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['deal-moved', 'add-deal'])
</script>

<template>
  <div class="flex gap-4 overflow-x-auto pb-4 h-full items-start">
    <KanbanColumn
      v-for="etapa in ETAPAS_ACTIVAS"
      :key="etapa"
      :etapa="etapa"
      :deals="pipeline[etapa] || []"
      @deal-moved="(dealId, newEtapa) => emit('deal-moved', dealId, newEtapa)"
      @add-deal="(etapa) => emit('add-deal', etapa)"
    />
  </div>
</template>
