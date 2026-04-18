import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value, currency = 'COP') {
  if (value === null || value === undefined || value === '') return '—'
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatDate(dateStr) {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '—'
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

export function formatRelativeDate(dateStr) {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '—'
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return 'Hoy'
  if (diffDays === 1) return 'Ayer'
  if (diffDays < 7) return `hace ${diffDays} días`
  if (diffDays < 30) return `hace ${Math.floor(diffDays / 7)} semanas`
  return formatDate(dateStr)
}

export function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

export const ETAPAS_ORDER = [
  'prospeccion',
  'primer_contacto',
  'oferta_enviada',
  'negociacion',
  'contrato',
  'cerrado_ganado',
  'cerrado_perdido',
  'sin_interes',
]

export const ETAPAS_CONFIG = {
  prospeccion: {
    label: 'Prospección',
    color: 'bg-slate-100 text-slate-700',
    dotColor: 'bg-slate-400',
    headerColor: 'bg-slate-50 border-slate-200',
  },
  primer_contacto: {
    label: 'Primer Contacto',
    color: 'bg-blue-100 text-blue-700',
    dotColor: 'bg-blue-400',
    headerColor: 'bg-blue-50 border-blue-200',
  },
  oferta_enviada: {
    label: 'Oferta Enviada',
    color: 'bg-yellow-100 text-yellow-700',
    dotColor: 'bg-yellow-400',
    headerColor: 'bg-yellow-50 border-yellow-200',
  },
  negociacion: {
    label: 'Negociación',
    color: 'bg-orange-100 text-orange-700',
    dotColor: 'bg-orange-400',
    headerColor: 'bg-orange-50 border-orange-200',
  },
  contrato: {
    label: 'Contrato',
    color: 'bg-purple-100 text-purple-700',
    dotColor: 'bg-purple-400',
    headerColor: 'bg-purple-50 border-purple-200',
  },
  cerrado_ganado: {
    label: 'Cerrado Ganado',
    color: 'bg-green-100 text-green-700',
    dotColor: 'bg-green-500',
    headerColor: 'bg-green-50 border-green-200',
  },
  cerrado_perdido: {
    label: 'Cerrado Perdido',
    color: 'bg-red-100 text-red-700',
    dotColor: 'bg-red-500',
    headerColor: 'bg-red-50 border-red-200',
  },
  sin_interes: {
    label: 'Sin Interés',
    color: 'bg-gray-100 text-gray-600',
    dotColor: 'bg-gray-400',
    headerColor: 'bg-gray-50 border-gray-200',
  },
}

export const SERVICIOS_CONFIG = {
  representacion: { label: 'Representación', color: 'bg-indigo-100 text-indigo-700' },
  cgm: { label: 'CGM', color: 'bg-indigo-100 text-indigo-700' },
  monitoreo: { label: 'Monitoreo', color: 'bg-cyan-100 text-cyan-700' },
  ppa: { label: 'PPA', color: 'bg-blue-100 text-blue-700' },
  venta_energia: { label: 'Venta Energía', color: 'bg-orange-100 text-orange-700' },
  recs: { label: 'RECs', color: 'bg-green-100 text-green-700' },
}

export const TIPO_ACTIVIDAD_CONFIG = {
  llamada: { label: 'Llamada', icon: 'Phone', color: 'text-blue-500 bg-blue-50' },
  reunion: { label: 'Reunión', icon: 'Users', color: 'text-purple-500 bg-purple-50' },
  email: { label: 'Email', icon: 'Mail', color: 'text-yellow-500 bg-yellow-50' },
  nota: { label: 'Nota', icon: 'FileText', color: 'text-gray-500 bg-gray-50' },
  cambio_etapa: { label: 'Cambio de Etapa', icon: 'ArrowRight', color: 'text-green-500 bg-green-50' },
  documento: { label: 'Documento', icon: 'Paperclip', color: 'text-orange-500 bg-orange-50' },
  tarea: { label: 'Tarea', icon: 'CheckSquare', color: 'text-indigo-500 bg-indigo-50' },
}

export const PRIORIDAD_CONFIG = {
  baja: { label: 'Baja', color: 'bg-gray-100 text-gray-600', dot: 'bg-gray-400' },
  media: { label: 'Media', color: 'bg-yellow-100 text-yellow-700', dot: 'bg-yellow-400' },
  alta: { label: 'Alta', color: 'bg-orange-100 text-orange-700', dot: 'bg-orange-500' },
  urgente: { label: 'Urgente', color: 'bg-red-100 text-red-700', dot: 'bg-red-500' },
}

export const DOCUMENTO_ESTADO_CONFIG = {
  pendiente: { label: 'Pendiente', color: 'bg-gray-100 text-gray-600' },
  recibido: { label: 'Recibido', color: 'bg-blue-100 text-blue-700' },
  aprobado: { label: 'Aprobado', color: 'bg-green-100 text-green-700' },
  vencido: { label: 'Vencido', color: 'bg-red-100 text-red-700' },
  rechazado: { label: 'Rechazado', color: 'bg-red-100 text-red-700' },
}

export const ROLES_CONFIG = {
  admin: { label: 'Administrador', color: 'bg-red-100 text-red-700' },
  manager_comercial: { label: 'Manager Comercial', color: 'bg-purple-100 text-purple-700' },
  comercial: { label: 'Comercial', color: 'bg-blue-100 text-blue-700' },
  operaciones: { label: 'Operaciones', color: 'bg-green-100 text-green-700' },
  viewer: { label: 'Visualizador', color: 'bg-gray-100 text-gray-600' },
}

export function getInitials(name) {
  if (!name) return '?'
  return name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase()
}

export function isOverdue(dateStr) {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}
