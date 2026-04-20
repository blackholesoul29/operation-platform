import { createRouter, createWebHistory } from 'vue-router'
import BlankLayout from '@/components/layout/BlankLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },

  // Info Técnica, CGM y Liquidaciones — pantalla en blanco (el shell los maneja)
  { path: '/proyectos',     name: 'proyectos',     component: BlankLayout },
  { path: '/cgm',           name: 'cgm',           component: BlankLayout },
  { path: '/liquidaciones', name: 'liquidaciones', component: BlankLayout },

  // Operaciones Comerciales — con menú horizontal
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '',                  name: 'dashboard',     component: () => import('@/views/DashboardView.vue') },
      { path: 'pipeline',          name: 'pipeline',      component: () => import('@/views/PipelineView.vue') },
      { path: 'deals',             name: 'deals',         component: () => import('@/views/deals/DealsView.vue') },
      { path: 'deals/nuevo',       name: 'deal-create',   component: () => import('@/views/deals/DealFormView.vue') },
      { path: 'deals/:id',         name: 'deal-detail',   component: () => import('@/views/deals/DealDetailView.vue') },
      { path: 'deals/:id/editar',  name: 'deal-edit',     component: () => import('@/views/deals/DealFormView.vue') },
      { path: 'clientes',          name: 'clientes',      component: () => import('@/views/clientes/ClientesView.vue') },
      { path: 'clientes/nuevo',    name: 'cliente-crear', component: () => import('@/views/clientes/CrearClienteView.vue') },
      { path: 'clientes/:id',      name: 'cliente-detail',component: () => import('@/views/clientes/ClienteDetailView.vue') },
      { path: 'documentos',        name: 'documentos',    component: () => import('@/views/documentos/DocumentosView.vue') },
      { path: 'tareas',            name: 'tareas',        component: () => import('@/views/tareas/TareasView.vue') },
      { path: 'notificaciones',    name: 'notificaciones',component: () => import('@/views/NotificacionesView.vue') },
      { path: 'admin/usuarios',    name: 'admin-usuarios',component: () => import('@/views/admin/UsersView.vue'), meta: { role: 'admin' } },
    ],
  },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('enerflow_access')
  const isAuthenticated = !!token

  if (!to.meta.public && !isAuthenticated) {
    return { name: 'login' }
  }

  if (to.name === 'login' && isAuthenticated) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
