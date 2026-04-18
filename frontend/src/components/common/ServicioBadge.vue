<script setup>
import { computed } from 'vue'
import { SERVICIOS_CONFIG } from '@/lib/utils'

const props = defineProps({
  servicio: { type: String, required: true },
  class: { type: String, default: '' },
})

const config = computed(() => SERVICIOS_CONFIG[props.servicio] || { label: props.servicio, color: 'bg-gray-100 text-gray-600' })
</script>

<template>
  <span
    :class="['inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold', config.color, props.class]"
  >
    {{ config.label }}
  </span>
</template>
