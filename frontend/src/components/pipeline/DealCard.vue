<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { AlertTriangle, Clock } from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'
import { formatCurrency, SERVICIOS_CONFIG, getInitials } from '@/lib/utils'

const props = defineProps({
  deal: { type: Object, required: true },
})

const router = useRouter()

const serviciosToShow = computed(() => {
  const s = props.deal.servicios || []
  return s.slice(0, 3)
})

const serviciosExtra = computed(() => {
  const s = props.deal.servicios || []
  return s.length > 3 ? s.length - 3 : 0
})

function onClick() {
  router.push(`/deals/${props.deal.id}`)
}

const assignedInitials = computed(() => {
  const u = props.deal.comercial_asignado
  if (!u) return '?'
  if (u.first_name) return getInitials(`${u.first_name} ${u.last_name || ''}`)
  return (u.username || '?').slice(0, 2).toUpperCase()
})

const assignedName = computed(() => {
  const u = props.deal.comercial_asignado
  if (!u) return ''
  if (u.first_name) return `${u.first_name} ${u.last_name || ''}`.trim()
  return u.username || ''
})
</script>

<template>
  <div
    :data-deal-id="deal.id"
    class="bg-white rounded-lg border border-slate-200 p-3 cursor-pointer hover:border-primary/40 hover:shadow-sm transition-all select-none"
    @click="onClick"
  >
    <!-- Client name -->
    <div class="flex items-start justify-between gap-2 mb-1">
      <p class="text-xs font-semibold text-slate-500 truncate">
        {{ deal.cliente?.nombre || deal.cliente_nombre || '—' }}
      </p>
      <div v-if="deal.documentos_pendientes > 0" class="flex-shrink-0">
        <span class="flex items-center gap-1 text-xs text-amber-600 bg-amber-50 rounded px-1.5 py-0.5">
          <AlertTriangle class="h-3 w-3" />
          {{ deal.documentos_pendientes }}
        </span>
      </div>
    </div>

    <!-- Deal name -->
    <p class="text-sm font-medium text-slate-800 leading-snug mb-2 line-clamp-2">
      {{ deal.nombre }}
    </p>

    <!-- Services -->
    <div v-if="serviciosToShow.length" class="flex flex-wrap gap-1 mb-2">
      <span
        v-for="svc in serviciosToShow"
        :key="svc"
        :class="['inline-flex items-center rounded-full px-1.5 py-0.5 text-[10px] font-semibold', SERVICIOS_CONFIG[svc]?.color || 'bg-gray-100 text-gray-600']"
      >
        {{ SERVICIOS_CONFIG[svc]?.label || svc }}
      </span>
      <span
        v-if="serviciosExtra > 0"
        class="inline-flex items-center rounded-full px-1.5 py-0.5 text-[10px] font-semibold bg-slate-100 text-slate-600"
      >
        +{{ serviciosExtra }}
      </span>
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between mt-1">
      <div class="flex items-center gap-2">
        <span class="text-xs font-semibold text-slate-600">
          {{ deal.valor_estimado ? formatCurrency(deal.valor_estimado) : '—' }}
        </span>
        <span
          v-if="deal.dias_en_etapa !== undefined"
          class="flex items-center gap-0.5 text-[10px] text-slate-400"
        >
          <Clock class="h-3 w-3" />
          {{ deal.dias_en_etapa }}d
        </span>
      </div>
      <Avatar
        v-if="assignedName"
        :fallback="assignedInitials"
        :alt="assignedName"
        size="sm"
        class="h-6 w-6 text-[10px]"
      />
    </div>
  </div>
</template>
