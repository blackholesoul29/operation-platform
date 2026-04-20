<template>
  <div class="platform">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="brand" v-if="!sidebarCollapsed">
          <div class="brand-icon">⚡</div>
          <div class="brand-text">
            <span class="brand-name">Plataforma</span>
            <span class="brand-sub">Operaciones</span>
          </div>
        </div>
        <div class="brand brand-sm" v-else>
          <div class="brand-icon">⚡</div>
        </div>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <ChevronLeft v-if="!sidebarCollapsed" :size="16" />
          <ChevronRight v-else :size="16" />
        </button>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-label" v-if="!sidebarCollapsed">MÓDULOS</div>

        <button
          v-for="mod in modules"
          :key="mod.id"
          class="nav-item"
          :class="{ active: activeModule === mod.id }"
          @click="switchModule(mod)"
          :title="sidebarCollapsed ? mod.label : ''"
        >
          <span class="nav-icon">{{ mod.icon }}</span>
          <span class="nav-label" v-if="!sidebarCollapsed">{{ mod.label }}</span>
          <span class="nav-status" :class="serviceStatus[mod.id]" v-if="!sidebarCollapsed"></span>
        </button>
      </nav>

      <div class="sidebar-footer" v-if="!sidebarCollapsed">
        <div class="status-panel">
          <div class="status-title">Estado de Servicios</div>
          <div v-for="mod in modules" :key="mod.id" class="status-row">
            <span class="status-dot" :class="serviceStatus[mod.id]"></span>
            <span class="status-label">{{ mod.label }}</span>
          </div>
        </div>
        <div class="footer-hint">
          <span>Rama:</span>
          <code>{{ activeModuleData?.branch }}</code>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <main class="main-area">
      <header class="topbar">
        <div class="topbar-left">
          <span class="current-module-icon">{{ activeModuleData?.icon }}</span>
          <div class="current-module-info">
            <span class="current-module-name">{{ activeModuleData?.label }}</span>
            <span class="current-module-branch">branch: {{ activeModuleData?.branch }}</span>
          </div>
        </div>
        <div class="topbar-right">
          <div class="service-badge" :class="iframeStatus">
            <span class="badge-dot"></span>
            <span>{{ iframeStatus === 'ok' ? 'Servicio activo' : iframeStatus === 'error' ? 'No disponible' : 'Conectando...' }}</span>
          </div>
          <button class="reload-btn" @click="reloadIframe" title="Recargar módulo">↻</button>
        </div>
      </header>

      <div class="module-container">
        <div class="loading-overlay" v-if="loading">
          <div class="loading-spinner"></div>
          <div class="loading-text">Cargando {{ activeModuleData?.label }}...</div>
          <div class="loading-sub">Asegúrate de haber ejecutado start.bat</div>
        </div>

        <div class="error-overlay" v-if="error && !loading">
          <div class="error-icon">🔌</div>
          <div class="error-title">Servicio apagado</div>
          <div class="error-msg">
            <strong>{{ activeModuleData?.label }}</strong> no está disponible en este momento.
          </div>
          <div class="error-steps">
            <div class="error-step">1. Verifica tu conexión a internet</div>
            <div class="error-step">2. Comprueba que el servicio esté desplegado correctamente</div>
            <div class="error-step">3. Presiona <strong>Reintentar</strong> en unos segundos</div>
          </div>
          <button class="retry-btn" @click="reloadIframe">↻ Reintentar</button>
        </div>

        <iframe
          v-for="mod in modules"
          v-show="frameReady[mod.id]"
          :key="mod.id"
          :ref="el => { if(el) iframeRefs[mod.id] = el }"
          :src="frameReady[mod.id] ? mod.url : 'about:blank'"
          :class="{ visible: activeModule === mod.id && frameReady[mod.id] }"
          class="module-frame"
          frameborder="0"
          allow="*"
        ></iframe>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const COMERCIAL_URL = import.meta.env.VITE_COMERCIAL_URL || 'http://localhost:5173'
const ANALISIS_URL  = import.meta.env.VITE_ANALISIS_URL  || 'http://localhost:5174'

const modules = [
  {
    id: 'monitoring',
    label: 'Monitoreo de Fallas',
    icon: '📊',
    branch: 'main',
    port: null,
    url: '/monitoring.html',
    local: true,
  },
  {
    id: 'comercial',
    label: 'Operaciones Comerciales',
    icon: '💼',
    branch: 'producto-operaciones',
    port: null,
    url: COMERCIAL_URL,
    local: false,
  },
  {
    id: 'proyectos',
    label: 'Info Técnica',
    icon: '⚡',
    branch: 'producto-operaciones',
    port: null,
    url: `${COMERCIAL_URL}/proyectos`,
    local: false,
  },
  {
    id: 'cgm',
    label: 'CGM',
    icon: '📋',
    branch: 'producto-operaciones',
    port: null,
    url: `${COMERCIAL_URL}/cgm`,
    local: false,
  },
  {
    id: 'liquidaciones',
    label: 'Liquidaciones',
    icon: '💰',
    branch: 'producto-operaciones',
    port: null,
    url: `${COMERCIAL_URL}/liquidaciones`,
    local: false,
  },
  {
    id: 'analisis',
    label: 'Análisis y Estrategia',
    icon: '📈',
    branch: 'jessi',
    port: null,
    url: ANALISIS_URL,
    local: false,
  },
]

const sidebarCollapsed = ref(false)
const activeModule = ref('monitoring')
const loading = ref(true)
const error = ref(false)
const iframeRefs = ref({})
const iframeStatus = ref('loading')
const serviceStatus = reactive({
  monitoring: 'ok', comercial: 'unknown',
  proyectos: 'unknown', cgm: 'unknown', liquidaciones: 'unknown', analisis: 'unknown',
})
const frameReady = reactive({
  monitoring: true, comercial: false,
  proyectos: false, cgm: false, liquidaciones: false, analisis: false,
})

const activeModuleData = computed(() => modules.find(m => m.id === activeModule.value))

async function checkService(mod) {
  if (mod.local) return true
  try {
    await fetch(mod.url, { mode: 'no-cors', signal: AbortSignal.timeout(4000) })
    return true
  } catch {
    return false
  }
}

async function loadModule(moduleId) {
  const mod = modules.find(m => m.id === moduleId)
  if (!mod) return

  loading.value = true
  error.value = false
  iframeStatus.value = 'loading'

  if (mod.local) {
    frameReady[moduleId] = true
    loading.value = false
    error.value = false
    iframeStatus.value = 'ok'
    serviceStatus[moduleId] = 'ok'
    return
  }

  const up = await checkService(mod)
  if (activeModule.value !== moduleId) return  // cambió de módulo mientras esperaba

  if (up) {
    frameReady[moduleId] = true
    serviceStatus[moduleId] = 'ok'
    iframeStatus.value = 'ok'
    loading.value = false
  } else {
    frameReady[moduleId] = false
    serviceStatus[moduleId] = 'error'
    iframeStatus.value = 'error'
    loading.value = false
    error.value = true
  }
}

function switchModule(mod) {
  if (activeModule.value === mod.id) return
  activeModule.value = mod.id
  error.value = false
  loadModule(mod.id)
}

function reloadIframe() {
  const mod = modules.find(m => m.id === activeModule.value)
  if (!mod) return
  frameReady[mod.id] = false
  loadModule(mod.id)
}

onMounted(() => loadModule('monitoring'))
</script>

<style scoped>
.platform {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: #2C2039;
  color: #FDFAF7;
  font-family: 'Lato', sans-serif;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: 240px;
  min-width: 240px;
  background: #1a1025;
  border-right: 1px solid #4A3560;
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease, min-width 0.25s ease;
  overflow: hidden;
}
.sidebar.collapsed { width: 60px; min-width: 60px; }

.sidebar-header {
  padding: 16px 14px;
  border-bottom: 1px solid #4A3560;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-height: 64px;
}
.brand { display: flex; align-items: center; gap: 10px; overflow: hidden; flex: 1; }
.brand-sm { justify-content: center; }

.brand-icon {
  width: 34px; height: 34px; min-width: 34px;
  border-radius: 9px;
  background: linear-gradient(135deg, #915BD8, #F6FF72);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}
.brand-text { display: flex; flex-direction: column; overflow: hidden; }
.brand-name { font-size: 13px; font-weight: 800; color: #F6FF72; white-space: nowrap; }
.brand-sub  { font-size: 10px; color: #A89EC0; white-space: nowrap; }

.collapse-btn {
  background: #362848; border: 1px solid #4A3560; color: #A89EC0;
  border-radius: 6px; width: 26px; height: 26px; min-width: 26px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; flex-shrink: 0; transition: all 0.18s;
}
.collapse-btn:hover { background: #422D57; color: #FDFAF7; border-color: #915BD8; }

/* ── Nav ── */
.sidebar-nav { flex: 1; padding: 12px 8px; display: flex; flex-direction: column; gap: 4px; }

.nav-section-label {
  font-size: 9px; font-weight: 800; color: #6B5F80;
  letter-spacing: 1px; text-transform: uppercase;
  padding: 4px 8px 8px;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px; border-radius: 9px; border: none;
  background: transparent; color: #A89EC0;
  font-family: 'Lato', sans-serif; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: all 0.18s; text-align: left; width: 100%;
}
.nav-item:hover { background: #362848; color: #FDFAF7; }
.nav-item.active {
  background: linear-gradient(135deg, #362848, #422D57);
  color: #FDFAF7; border: 1px solid #5B4272;
  box-shadow: 0 2px 8px #00000040;
}
.nav-icon { font-size: 18px; min-width: 22px; text-align: center; }
.nav-label { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.nav-status { width: 7px; height: 7px; border-radius: 50%; background: #6B5F80; flex-shrink: 0; }
.nav-status.ok { background: #4ADE80; }
.nav-status.error { background: #FF5757; }
.nav-status.unknown { background: #F6FF72; animation: blink 1.2s infinite; }

/* ── Footer ── */
.sidebar-footer { padding: 12px; border-top: 1px solid #4A3560; }

.status-panel {
  background: #362848; border: 1px solid #4A3560;
  border-radius: 9px; padding: 10px 12px; margin-bottom: 10px;
}
.status-title { font-size: 9px; font-weight: 800; color: #6B5F80; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
.status-row { display: flex; align-items: center; gap: 7px; font-size: 11px; color: #A89EC0; margin-bottom: 5px; }
.status-row:last-child { margin-bottom: 0; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: #6B5F80; flex-shrink: 0; }
.status-dot.ok { background: #4ADE80; animation: pulse-green 2s infinite; }
.status-dot.error { background: #FF5757; }
.status-dot.unknown { background: #F6FF72; animation: blink 1.2s infinite; }
.status-label { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.status-port { font-family: monospace; font-size: 10px; color: #5B4272; }

.footer-hint { font-size: 10px; color: #6B5F80; display: flex; align-items: center; gap: 6px; }
.footer-hint code { background: #362848; border: 1px solid #4A3560; border-radius: 4px; padding: 1px 6px; color: #F6FF72; font-size: 10px; }

/* ── Main Area ── */
.main-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: #2C2039; }

.topbar {
  height: 56px; background: #1a1025; border-bottom: 1px solid #4A3560;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; gap: 12px; flex-shrink: 0;
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.current-module-icon { font-size: 22px; }
.current-module-info { display: flex; flex-direction: column; }
.current-module-name { font-size: 14px; font-weight: 700; color: #FDFAF7; }
.current-module-branch { font-size: 10px; color: #6B5F80; font-family: monospace; }

.topbar-right { display: flex; align-items: center; gap: 10px; }

.service-badge {
  display: flex; align-items: center; gap: 7px;
  padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; border: 1px solid;
}
.service-badge.ok     { background: #4ade8015; border-color: #4ade8040; color: #4ADE80; }
.service-badge.loading,
.service-badge.unknown { background: #f6ff7215; border-color: #f6ff7240; color: #F6FF72; }
.service-badge.error  { background: #ff575715; border-color: #ff575740; color: #FF5757; }
.badge-dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.service-badge.ok .badge-dot { animation: pulse-green 2s infinite; }
.service-badge.loading .badge-dot,
.service-badge.unknown .badge-dot { animation: blink 1s infinite; }

.reload-btn {
  background: #362848; border: 1px solid #4A3560; color: #A89EC0;
  border-radius: 8px; width: 34px; height: 34px; font-size: 18px;
  cursor: pointer; transition: all 0.18s; display: flex; align-items: center; justify-content: center;
}
.reload-btn:hover { background: #422D57; color: #FDFAF7; border-color: #915BD8; }

/* ── Module Container ── */
.module-container { flex: 1; position: relative; overflow: hidden; }

.module-frame {
  position: absolute; inset: 0; width: 100%; height: 100%;
  border: none; background: #2C2039;
  opacity: 0; pointer-events: none; transition: opacity 0.25s ease;
}
.module-frame.visible { opacity: 1; pointer-events: all; }

.loading-overlay, .error-overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: #2C2039; z-index: 10; gap: 12px;
}
.loading-spinner {
  width: 44px; height: 44px;
  border: 3px solid #4A3560; border-top-color: #915BD8;
  border-radius: 50%; animation: spin 0.9s linear infinite;
}
.loading-text { font-size: 16px; font-weight: 700; color: #FDFAF7; }
.loading-sub  { font-size: 12px; color: #6B5F80; }

.error-icon  { font-size: 48px; }
.error-title { font-size: 18px; font-weight: 800; color: #FF5757; }
.error-msg   { font-size: 13px; color: #A89EC0; }

.error-steps {
  background: #362848; border: 1px solid #4A3560; border-radius: 10px;
  padding: 14px 18px; margin-top: 8px; display: flex; flex-direction: column; gap: 8px;
}
.error-step { font-size: 12px; color: #A89EC0; }
.error-step code { background: #422D57; border: 1px solid #5B4272; border-radius: 4px; padding: 1px 7px; color: #F6FF72; font-size: 11px; }

.retry-btn {
  margin-top: 8px; background: #915BD8; color: #FDFAF7; border: none;
  border-radius: 9px; padding: 10px 24px; font-size: 13px; font-weight: 700;
  cursor: pointer; font-family: 'Lato', sans-serif; transition: all 0.18s;
}
.retry-btn:hover { background: #7d4ec0; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse-green { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }
</style>
