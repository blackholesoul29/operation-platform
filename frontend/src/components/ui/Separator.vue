<script setup>
import { cn } from '@/lib/utils'
const props = defineProps({
  orientation: { type: String, default: 'horizontal' },
  class: { type: String, default: '' },
})
</script>
<template>
  <div
    :class="cn(
      'shrink-0 bg-border',
      props.orientation === 'vertical' ? 'h-full w-[1px]' : 'h-[1px] w-full',
      props.class
    )"
  />
</template>
