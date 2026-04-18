<script setup>
const props = defineProps({
  title: { type: String, default: 'Sin resultados' },
  description: { type: String, default: '' },
  icon: { type: Object, default: null },
})
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 text-center">
    <div v-if="icon || $slots.icon" class="mb-4 rounded-full bg-muted p-4">
      <component
        :is="icon"
        v-if="icon"
        class="h-8 w-8 text-muted-foreground"
      />
      <slot v-else name="icon" />
    </div>
    <h3 class="text-base font-semibold text-foreground mb-1">{{ title }}</h3>
    <p v-if="description" class="text-sm text-muted-foreground max-w-sm">{{ description }}</p>
    <div v-if="$slots.default" class="mt-4">
      <slot />
    </div>
  </div>
</template>
