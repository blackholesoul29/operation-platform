<script setup>
import { cn } from '@/lib/utils'
import { ChevronDown } from 'lucide-vue-next'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Seleccionar...' },
  disabled: { type: Boolean, default: false },
  class: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="relative w-full">
    <select
      v-bind="$attrs"
      :value="modelValue"
      :disabled="disabled"
      :class="cn(
        'flex h-9 w-full appearance-none rounded-md border border-input bg-background px-3 py-1 pr-8 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
        props.class
      )"
      @change="emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>{{ placeholder }}</option>
      <option
        v-for="opt in options"
        :key="opt.value"
        :value="opt.value"
      >
        {{ opt.label }}
      </option>
    </select>
    <ChevronDown
      class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"
    />
  </div>
</template>
