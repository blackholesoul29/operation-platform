<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Zap, Eye, EyeOff } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Spinner from '@/components/ui/Spinner.vue'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

async function handleLogin() {
  if (!form.username.trim() || !form.password) {
    error.value = 'Por favor completa todos los campos'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await auth.login(form.username, form.password)
    router.push('/')
  } catch (e) {
    if (e.response?.status === 401) {
      error.value = 'Credenciales incorrectas. Verifica tu usuario y contraseña.'
    } else {
      error.value = 'Error al conectar con el servidor. Intenta de nuevo.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-950 to-slate-800 p-4">
    <!-- Background decoration -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-1/2 -right-1/4 w-[800px] h-[800px] rounded-full bg-blue-500/5 blur-3xl" />
      <div class="absolute -bottom-1/4 -left-1/4 w-[600px] h-[600px] rounded-full bg-indigo-500/5 blur-3xl" />
    </div>

    <div class="relative w-full max-w-md">
      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
        <!-- Header -->
        <div class="bg-gradient-to-br from-slate-800 to-blue-900 px-8 py-8 text-center">
          <div class="flex items-center justify-center gap-3 mb-3">
            <div class="flex items-center justify-center h-12 w-12 rounded-xl bg-primary shadow-lg">
              <Zap class="h-7 w-7 text-white" />
            </div>
          </div>
          <h1 class="text-3xl font-bold text-white tracking-tight">EnerFlow</h1>
          <p class="text-blue-200 text-sm mt-1">Plataforma de Operaciones Energéticas</p>
        </div>

        <!-- Form -->
        <div class="px-8 py-8">
          <h2 class="text-xl font-semibold text-foreground mb-6">Iniciar sesión</h2>

          <form class="space-y-4" @submit.prevent="handleLogin">
            <!-- Error -->
            <Transition
              enter-active-class="transition duration-200"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
            >
              <div
                v-if="error"
                class="flex items-center gap-2 rounded-lg bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive"
              >
                <svg class="h-4 w-4 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
                </svg>
                {{ error }}
              </div>
            </Transition>

            <!-- Username -->
            <div class="space-y-1.5">
              <Label for="username">Correo Unergy</Label>
              <Input
                id="username"
                v-model="form.username"
                type="text"
                placeholder="nombre@unergy.io"
                autocomplete="username"
                :disabled="loading"
              />
            </div>

            <!-- Password -->
            <div class="space-y-1.5">
              <Label for="password">Contraseña</Label>
              <div class="relative">
                <Input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="••••••••"
                  autocomplete="current-password"
                  :disabled="loading"
                  class="pr-10"
                />
                <button
                  type="button"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  @click="showPassword = !showPassword"
                >
                  <Eye v-if="!showPassword" class="h-4 w-4" />
                  <EyeOff v-else class="h-4 w-4" />
                </button>
              </div>
            </div>

            <!-- Submit -->
            <Button
              type="submit"
              class="w-full h-10"
              :disabled="loading"
            >
              <Spinner v-if="loading" size="sm" class="mr-2" />
              {{ loading ? 'Iniciando sesión...' : 'Iniciar sesión' }}
            </Button>
          </form>

          <p class="text-center text-xs text-muted-foreground mt-6">
            EnerFlow — Plataforma Comercial Energética &copy; 2025
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
