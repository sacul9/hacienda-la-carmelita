<template>
  <div class="min-h-screen flex items-center justify-center bg-crema-50 px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <NuxtLink to="/">
          <h1 class="font-display text-2xl font-bold text-tierra-800">🏡 Hacienda La Carmelita</h1>
          <p class="text-sm text-gray-500 mt-1">Panel de Administración</p>
        </NuxtLink>
      </div>

      <BaseCard :padding="false">
        <div class="p-8">
          <h2 class="text-xl font-semibold text-gray-900 mb-6">Iniciar sesión</h2>
          <form class="space-y-4" @submit.prevent="handleLogin">
            <BaseInput v-model="form.email" label="Correo electrónico" type="email"
              placeholder="admin@haciendalacarmelita.com" required :error="errors.email" />
            <BaseInput v-model="form.password" label="Contraseña" type="password"
              placeholder="••••••••" required :error="errors.password" />
            <div v-if="errorLogin" class="bg-red-50 border border-red-200 rounded-lg p-3">
              <p class="text-sm text-red-700">{{ errorLogin }}</p>
            </div>
            <BaseButton type="submit" class="w-full" size="lg" :loading="authLoading">
              Ingresar al panel
            </BaseButton>
          </form>
          <div class="mt-6 pt-6 border-t border-gray-100 text-center">
            <NuxtLink to="/" class="text-sm text-tierra-700 hover:text-tierra-900">← Volver al sitio</NuxtLink>
          </div>
        </div>
      </BaseCard>
      <p class="text-center text-xs text-gray-400 mt-6">🔒 Sesión protegida con JWT + 2FA</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })
useSeoMeta({ title: 'Admin — Hacienda La Carmelita', robots: 'noindex' })

const { login, loading } = useAuth()
const authLoading = computed(() => loading.value)

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })
const errorLogin = ref('')

const validar = () => {
  errors.email = !form.email ? 'El correo es obligatorio' : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) ? 'Correo inválido' : ''
  errors.password = !form.password ? 'La contraseña es obligatoria' : ''
  return !errors.email && !errors.password
}

const handleLogin = async () => {
  if (!validar()) return
  errorLogin.value = ''
  try {
    await login(form.email, form.password)
  } catch (e: any) {
    errorLogin.value = e?.data?.detail ?? 'Credenciales inválidas'
  }
}
</script>
