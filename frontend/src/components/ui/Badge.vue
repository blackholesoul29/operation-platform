<script setup>
import { cn } from '@/lib/utils'
import { cva } from 'class-variance-authority'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground',
        secondary: 'border-transparent bg-secondary text-secondary-foreground',
        destructive: 'border-transparent bg-destructive text-destructive-foreground',
        outline: 'text-foreground',
        success: 'border-transparent bg-green-100 text-green-700',
        warning: 'border-transparent bg-yellow-100 text-yellow-700',
      },
    },
    defaultVariants: { variant: 'default' },
  }
)

const props = defineProps({
  variant: { type: String, default: 'default' },
  class: { type: String, default: '' },
})
</script>

<template>
  <span :class="cn(badgeVariants({ variant }), props.class)">
    <slot />
  </span>
</template>
