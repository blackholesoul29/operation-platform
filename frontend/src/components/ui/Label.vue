<script setup>
import { cn } from '@/lib/utils'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  class: { type: String, default: '' },
})
</script>

<template>
  <label
    v-bind="$attrs"
    :class="cn('text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70', props.class)"
  >
    <slot />
  </label>
</template>
