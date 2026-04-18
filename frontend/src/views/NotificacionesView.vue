<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificacionesStore } from '@/stores/notificaciones'
import {
  Bell, CheckCheck, Briefcase, Building2, FileText, AlertCircle, Info, CheckCircle
} from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { formatRelativeDate } from '@/lib/utils'

const store = useNotificacionesStore()
const router = useRouter()

onMounted(() => store.fetchNotificaciones())

function iconForType(tipo) {
  const map = {
    deal: Briefcase,
    cliente: Building2,
    documento: FileText,
    tarea: CheckCircle,
    alerta: AlertCircle,
    sistema: Info,
  }
  return map[tipo] || Bell
}

function colorForType(tipo) {
  const map = {
    deal: 'bg-blue-100 text-blue-600',
    cliente: 'bg-green-100 text-green-600',
    documento: 'bg-orange-100 text-orange-600',
    tarea: 'bg-purple-100 text-purple-600',
    alerta: 'bg-red-100 text-red-600',
    sistema: 'bg-gray-100 text-gray-600',
  }
  return map[tipo] || 'bg-gray-100 text-gray-600'
}

async function clickNotif(notif) {
  if (!notif.leida) await store.marcarLeida(notif.id)
  if (notif.link) router.push(notif.link)
  else if (notif.deal) router.push(`/deals/${notif.deal}`)
  else if (notif.cliente) router.push(`/clientes/${notif.cliente}`)
}

const unreadCount = computed(() => store.notificaciones.filter(n => !n.leida).length)
</script>

<template>
  <div class="max-w-3xl mx-auto space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Notificaciones</h1>
        <p v-if="unreadCount" class="text-sm text-muted-foreground mt-0.5">
          {{ unreadCount }} sin leer
        </p>
      </div>
      <Button
        v-if="unreadCount > 0"
        variant="outline"
        size="sm"
        @click="store.marcarTodasLeidas()"
      >
        <CheckCheck class="h-4 w-4 mr-1" />
        Marcar todas como leídas
      </Button>
    </div>

    <div v-if="store.loading" class="flex justify-center py-12">
      <Spinner size="lg" />
    </div>

    <EmptyState
      v-else-if="!store.notificaciones.length"
      :icon="Bell"
      title="Sin notificaciones"
      description="No tienes notificaciones en este momento."
    />

    <div v-else class="space-y-2">
      <div
        v-for="notif in store.notificaciones"
        :key="notif.id"
        :class="[
          'flex items-start gap-4 rounded-xl border p-4 cursor-pointer transition-all',
          !notif.leida
            ? 'bg-blue-50 border-blue-100 hover:bg-blue-100/60'
            : 'bg-card hover:bg-muted/40',
        ]"
        @click="clickNotif(notif)"
      >
        <!-- Icon -->
        <div :class="['flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full', colorForType(notif.tipo)]">
          <component :is="iconForType(notif.tipo)" class="h-5 w-5" />
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2">
            <p :class="['text-sm leading-snug', !notif.leida ? 'font-semibold text-foreground' : 'font-medium text-foreground']">
              {{ notif.titulo || notif.mensaje }}
            </p>
            <div class="flex items-center gap-2 flex-shrink-0">
              <span class="text-xs text-muted-foreground whitespace-nowrap">{{ formatRelativeDate(notif.created_at) }}</span>
              <span v-if="!notif.leida" class="h-2 w-2 rounded-full bg-primary flex-shrink-0" />
            </div>
          </div>
          <p v-if="notif.titulo && notif.mensaje" class="text-sm text-muted-foreground mt-0.5 line-clamp-2">
            {{ notif.mensaje }}
          </p>
          <div class="flex items-center gap-2 mt-1.5">
            <span v-if="notif.deal_nombre" class="flex items-center gap-1 text-xs text-muted-foreground">
              <Briefcase class="h-3 w-3" /> {{ notif.deal_nombre }}
            </span>
            <span v-if="notif.cliente_nombre" class="flex items-center gap-1 text-xs text-muted-foreground">
              <Building2 class="h-3 w-3" /> {{ notif.cliente_nombre }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
