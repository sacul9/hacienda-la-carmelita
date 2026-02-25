<template>
  <div class="min-h-screen flex items-center justify-center bg-crema-50 px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <NuxtLink to="/"><h1 class="font-display text-xl font-bold text-tierra-800">🏡 Hacienda La Carmelita</h1></NuxtLink>
      </div>
      <BaseCard :padding="false">
        <div class="p-8">
          <OTPVerificacion
            :email="email"
            :telefono="telefono"
            :usuario-id="usuarioId"
            :proposito="proposito"
            @verificado="onVerificado"
            @error="onError"
          />
        </div>
      </BaseCard>
      <div class="mt-6 text-center">
        <NuxtLink to="/" class="text-sm text-tierra-700 hover:text-tierra-900">← Cancelar</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })
useSeoMeta({ title: 'Verificación — Hacienda La Carmelita', robots: 'noindex' })

const route = useRoute()
const router = useRouter()
const bookingStore = useBookingStore()

const email = computed(() => (route.query.email as string) ?? bookingStore.huesped?.email ?? '')
const telefono = computed(() => (route.query.telefono as string) ?? bookingStore.huesped?.telefono ?? '')
const usuarioId = computed(() => route.query.usuario_id as string ?? '')
const proposito = computed(() => (route.query.proposito as any) ?? 'reserva')

const onVerificado = async (token: string) => {
  bookingStore.confirmarOTP(token)
  if (proposito.value === 'reserva') await router.push('/reservar/pago')
  else if (proposito.value === 'login') await router.push('/admin/dashboard')
  else await router.push('/')
}

const onError = (mensaje: string) => console.warn('[OTP]', mensaje)
</script>
