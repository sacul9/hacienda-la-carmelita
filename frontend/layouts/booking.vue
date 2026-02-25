<template>
  <div class="min-h-screen bg-crema-50">
    <!-- Header simplificado para el flujo de reserva -->
    <header class="bg-white border-b border-gray-100 py-4">
      <div class="container-site flex items-center justify-between">
        <NuxtLink to="/" class="font-display text-xl font-semibold text-tierra-800">
          Hacienda La Carmelita
        </NuxtLink>
        <!-- Stepper de pasos -->
        <BookingStepper :current-step="currentStep" />
      </div>
    </header>
    <main class="container-site py-8 max-w-4xl">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const currentStep = computed(() => {
  const stepMap: Record<string, number> = {
    '/reservar': 1,
    '/reservar/experiencias': 2,
    '/reservar/datos': 3,
    '/reservar/verificar': 4,
    '/reservar/pago': 5,
    '/reservar/confirmacion': 6,
  }
  return stepMap[route.path] ?? 1
})
</script>
