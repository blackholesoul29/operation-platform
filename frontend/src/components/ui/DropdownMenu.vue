<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  align: { type: String, default: 'right' },
})

const emit = defineEmits(['select'])

const open = ref(false)
const triggerRef = ref(null)
const menuRef = ref(null)

function toggle() {
  open.value = !open.value
}

function handleAction(item) {
  if (item.action) item.action()
  emit('select', item)
  open.value = false
}

function handleClickOutside(e) {
  if (
    triggerRef.value &&
    !triggerRef.value.contains(e.target) &&
    menuRef.value &&
    !menuRef.value.contains(e.target)
  ) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div class="relative inline-block">
    <div ref="triggerRef" @click.stop="toggle">
      <slot name="trigger" />
    </div>

    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="open"
        ref="menuRef"
        :class="[
          'absolute z-50 mt-1 min-w-[10rem] overflow-hidden rounded-md border bg-background shadow-md',
          align === 'right' ? 'right-0' : 'left-0',
        ]"
      >
        <div class="p-1">
          <template v-for="(item, idx) in items" :key="idx">
            <div v-if="item.separator" class="my-1 h-px bg-border" />
            <button
              v-else
              class="flex w-full items-center gap-2 rounded-sm px-3 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              :class="item.destructive ? 'text-destructive hover:text-destructive' : ''"
              :disabled="item.disabled"
              @click="handleAction(item)"
            >
              <component :is="item.icon" v-if="item.icon" class="h-4 w-4" />
              {{ item.label }}
            </button>
          </template>
        </div>
      </div>
    </Transition>
  </div>
</template>
