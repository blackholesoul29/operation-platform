<script setup>
import { computed } from 'vue'
import { Trash2, Clock, Briefcase, Building2, Edit2 } from 'lucide-vue-next'
import { useTareasStore } from '@/stores/tareas'
import { formatDate, isOverdue, PRIORIDAD_CONFIG } from '@/lib/utils'

const props = defineProps({
  tarea: { type: Object, required: true },
})

const emit = defineEmits(['edit', 'deleted'])

const tareasStore = useTareasStore()

const prioridadConfig = computed(() => PRIORIDAD_CONFIG[props.tarea.prioridad] || PRIORIDAD_CONFIG.media)

const overdue = computed(() =>
  !props.tarea.completada && props.tarea.fecha_limite && isOverdue(props.tarea.fecha_limite)
)

async function toggleComplete() {
  if (props.tarea.completada) return
  await tareasStore.completarTarea(props.tarea.id)
}

async function deleteTarea() {
  await tareasStore.deleteTarea(props.tarea.id)
  emit('deleted', props.tarea.id)
}
</script>

<template>
  <div
    :class="[
      'flex items-start gap-3 rounded-lg border p-3 transition-colors',
      tarea.completada ? 'bg-muted/30 opacity-60' : 'bg-background hover:bg-muted/20',
    ]"
  >
    <!-- Checkbox -->
    <button
      :class="[
        'mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border-2 transition-all',
        tarea.completada
          ? 'border-green-500 bg-green-500 text-white'
          : 'border-border hover:border-primary',
      ]"
      @click="toggleComplete"
    >
      <svg v-if="tarea.completada" class="h-3 w-3" viewBox="0 0 12 12" fill="none">
        <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <!-- Priority dot -->
    <span :class="['mt-1.5 h-2 w-2 flex-shrink-0 rounded-full', prioridadConfig.dot]" :title="prioridadConfig.label" />

    <!-- Content -->
    <div class="flex-1 min-w-0">
      <p :class="['text-sm font-medium leading-snug', tarea.completada ? 'line-through text-muted-foreground' : 'text-foreground']">
        {{ tarea.titulo }}
      </p>
      <p v-if="tarea.descripcion" class="text-xs text-muted-foreground mt-0.5 line-clamp-1">
        {{ tarea.descripcion }}
      </p>

      <!-- Meta row -->
      <div class="flex flex-wrap items-center gap-3 mt-1.5">
        <span
          v-if="tarea.fecha_limite"
          :class="['flex items-center gap-1 text-xs', overdue ? 'text-destructive font-semibold' : 'text-muted-foreground']"
        >
          <Clock class="h-3 w-3" />
          {{ formatDate(tarea.fecha_limite) }}
          <span v-if="overdue" class="text-destructive">(Vencida)</span>
        </span>

        <span v-if="tarea.deal" class="flex items-center gap-1 text-xs text-muted-foreground">
          <Briefcase class="h-3 w-3" />
          {{ tarea.deal?.nombre || `Deal #${tarea.deal}` }}
        </span>

        <span v-if="tarea.cliente" class="flex items-center gap-1 text-xs text-muted-foreground">
          <Building2 class="h-3 w-3" />
          {{ tarea.cliente?.nombre || `Cliente #${tarea.cliente}` }}
        </span>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-1 flex-shrink-0">
      <button
        class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
        title="Editar"
        @click="emit('edit', tarea)"
      >
        <Edit2 class="h-3.5 w-3.5" />
      </button>
      <button
        class="p-1.5 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
        title="Eliminar"
        @click="deleteTarea"
      >
        <Trash2 class="h-3.5 w-3.5" />
      </button>
    </div>
  </div>
</template>
