<script setup>
import { cn, getInitials } from '@/lib/utils'

const props = defineProps({
  src: { type: String, default: '' },
  alt: { type: String, default: '' },
  fallback: { type: String, default: '' },
  size: { type: String, default: 'md' },
  class: { type: String, default: '' },
})

const sizeClasses = {
  sm: 'h-7 w-7 text-xs',
  md: 'h-9 w-9 text-sm',
  lg: 'h-12 w-12 text-base',
  xl: 'h-16 w-16 text-lg',
}

const colors = [
  'bg-blue-500',
  'bg-purple-500',
  'bg-green-500',
  'bg-orange-500',
  'bg-pink-500',
  'bg-indigo-500',
  'bg-teal-500',
  'bg-red-500',
]

function getColor(name) {
  if (!name) return colors[0]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const displayInitials = props.fallback || getInitials(props.alt)
</script>

<template>
  <div
    :class="cn(
      'rounded-full overflow-hidden flex items-center justify-center flex-shrink-0',
      sizeClasses[size] || sizeClasses.md,
      !src ? getColor(fallback || alt) : 'bg-muted',
      props.class
    )"
  >
    <img
      v-if="src"
      :src="src"
      :alt="alt"
      class="h-full w-full object-cover"
      @error="$event.target.style.display = 'none'"
    />
    <span v-else class="font-semibold text-white leading-none">
      {{ displayInitials }}
    </span>
  </div>
</template>
