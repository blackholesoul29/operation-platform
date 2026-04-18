<script setup>
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Button from '@/components/ui/Button.vue'
import { AlertTriangle } from 'lucide-vue-next'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '¿Estás seguro?' },
  description: { type: String, default: 'Esta acción no se puede deshacer.' },
  confirmLabel: { type: String, default: 'Confirmar' },
  cancelLabel: { type: String, default: 'Cancelar' },
  destructive: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel', 'update:open'])

function confirm() {
  emit('confirm')
}

function cancel() {
  emit('cancel')
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" size="sm" @update:open="emit('update:open', $event)">
    <DialogHeader>
      <div class="flex items-center gap-3">
        <div :class="['flex h-10 w-10 items-center justify-center rounded-full flex-shrink-0', destructive ? 'bg-red-100' : 'bg-amber-100']">
          <AlertTriangle :class="['h-5 w-5', destructive ? 'text-destructive' : 'text-amber-600']" />
        </div>
        <div>
          <DialogTitle>{{ title }}</DialogTitle>
          <p v-if="description" class="text-sm text-muted-foreground mt-1">{{ description }}</p>
        </div>
      </div>
    </DialogHeader>
    <DialogFooter>
      <Button variant="outline" :disabled="loading" @click="cancel">
        {{ cancelLabel }}
      </Button>
      <Button
        :variant="destructive ? 'destructive' : 'default'"
        :disabled="loading"
        @click="confirm"
      >
        <span v-if="loading" class="mr-2">
          <span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        </span>
        {{ confirmLabel }}
      </Button>
    </DialogFooter>
  </Dialog>
</template>
