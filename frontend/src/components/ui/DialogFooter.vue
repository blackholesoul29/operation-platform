<script setup>
import { cn } from '@/lib/utils'
const props = defineProps({ class: { type: String, default: '' } })
</script>
<template>
  <div :class="cn('flex items-center justify-end gap-3 p-6 pt-0', props.class)">
    <slot />
  </div>
</template>
