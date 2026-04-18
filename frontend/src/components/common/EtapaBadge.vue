<script setup>
import { computed } from 'vue'
import { ETAPAS_CONFIG } from '@/lib/utils'

const props = defineProps({
  etapa: { type: String, required: true },
  class: { type: String, default: '' },
})

const config = computed(() => ETAPAS_CONFIG[props.etapa] || { label: props.etapa, color: 'bg-gray-100 text-gray-600', dotColor: 'bg-gray-400' })
</script>

<template>
  <span
    :class="['inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold', config.color, props.class]"
  >
    <span :class="['h-1.5 w-1.5 rounded-full flex-shrink-0', config.dotColor]" />
    {{ config.label }}
  </span>
</template>
