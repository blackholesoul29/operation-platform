<script setup>
import { X } from 'lucide-vue-next'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
})

const emit = defineEmits(['update:open'])

function close() {
  emit('update:open', false)
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="open" class="fixed inset-0 z-50 flex justify-end">
        <!-- Overlay -->
        <div class="absolute inset-0 bg-black/40" @click="close" />

        <!-- Panel -->
        <Transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="translate-x-full"
          enter-to-class="translate-x-0"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="translate-x-0"
          leave-to-class="translate-x-full"
        >
          <div
            v-if="open"
            class="relative z-10 h-full w-full max-w-lg bg-background border-l shadow-xl flex flex-col"
          >
            <!-- Header -->
            <div class="flex items-center justify-between p-6 border-b">
              <h2 class="text-lg font-semibold">{{ title }}</h2>
              <button
                class="rounded-sm opacity-70 hover:opacity-100 transition-opacity"
                @click="close"
              >
                <X class="h-5 w-5" />
              </button>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto p-6">
              <slot />
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="border-t p-6">
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
