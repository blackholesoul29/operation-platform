<script setup>
import { cn } from '@/lib/utils'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: { type: String, default: '' },
  class: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <textarea
    v-bind="$attrs"
    :value="modelValue"
    :class="cn(
      'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 resize-none',
      props.class
    )"
    @input="emit('update:modelValue', $event.target.value)"
  />
</template>
