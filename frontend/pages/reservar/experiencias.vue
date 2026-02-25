<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-3xl font-display font-bold text-tierra-800">Elige tu experiencia</h1>
      <p class="text-gray-500 mt-2">Personaliza tu estadía en Hacienda La Carmelita</p>
    </div>

    <!-- Resumen de fechas -->
    <div class="flex items-center justify-center gap-3 flex-wrap">
      <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-tierra-50 text-tierra-800 border border-tierra-200">
        Check-in: {{ fechaFormateada(bookingStore.fechaCheckin) }}
      </span>
      <span class="text-gray-300">→</span>
      <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-tierra-50 text-tierra-800 border border-tierra-200">
        Check-out: {{ fechaFormateada(bookingStore.fechaCheckout) }}
      </span>
      <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-dorado-50 text-dorado-700 border border-dorado-200">
        {{ bookingStore.noches }} {{ bookingStore.noches === 1 ? 'noche' : 'noches' }}
      </span>
    </div>

    <!-- Paquete base -->
    <div>
      <h2 class="text-base font-semibold text-tierra-800 mb-3">Paquete incluido</h2>
      <BaseCard class="p-5 border-2 border-tierra-700 bg-tierra-50/30">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-start gap-4">
            <div class="text-4xl leading-none shrink-0">🏡</div>
            <div>
              <div class="flex items-center gap-2 mb-1">
                <h3 class="font-semibold text-tierra-800">Hacienda Completa</h3>
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-tierra-800 text-white">
                  ✓ Seleccionado
                </span>
              </div>
              <p class="text-sm text-gray-600 mb-3">
                Acceso completo a la hacienda: todas las habitaciones, piscina, zonas verdes, cocina equipada y áreas comunes.
              </p>
              <ul class="grid grid-cols-1 sm:grid-cols-2 gap-1 text-xs text-gray-500">
                <li class="flex items-center gap-1.5">
                  <span class="text-tierra-700 font-bold">✓</span> Piscina privada
                </li>
                <li class="flex items-center gap-1.5">
                  <span class="text-tierra-700 font-bold">✓</span> Zonas verdes
                </li>
                <li class="flex items-center gap-1.5">
                  <span class="text-tierra-700 font-bold">✓</span> Cocina equipada
                </li>
                <li class="flex items-center gap-1.5">
                  <span class="text-tierra-700 font-bold">✓</span> WiFi de alta velocidad
                </li>
                <li class="flex items-center gap-1.5">
                  <span class="text-tierra-700 font-bold">✓</span> Estacionamiento
                </li>
              </ul>
            </div>
          </div>
        </div>
        <p class="text-xs text-gray-400 mt-3 pt-3 border-t border-tierra-100">
          El precio total se calculará en el siguiente paso según las fechas seleccionadas.
        </p>
      </BaseCard>
    </div>

    <!-- Add-ons opcionales -->
    <div>
      <h2 class="text-base font-semibold text-tierra-800 mb-1">Experiencias adicionales <span class="font-normal text-gray-400 text-sm">(opcionales)</span></h2>
      <p class="text-sm text-gray-500 mb-3">Enriquece tu estadía con estas experiencias exclusivas de la hacienda.</p>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <button
          v-for="addon in addonsDisponibles"
          :key="addon.id"
          type="button"
          :class="[
            'text-left rounded-2xl border-2 p-4 transition-all duration-200 cursor-pointer',
            estaSeleccionado(addon.id)
              ? 'border-tierra-700 bg-tierra-50/50 shadow-sm'
              : 'border-gray-200 bg-white hover:border-tierra-300 hover:shadow-sm'
          ]"
          @click="bookingStore.toggleAddOn(addon)"
        >
          <div class="flex items-start justify-between gap-2 mb-2">
            <span class="text-2xl leading-none">{{ addon.emoji }}</span>
            <div
              :class="[
                'w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors',
                estaSeleccionado(addon.id)
                  ? 'border-tierra-700 bg-tierra-700'
                  : 'border-gray-300 bg-white'
              ]"
            >
              <span v-if="estaSeleccionado(addon.id)" class="text-white text-xs leading-none font-bold">✓</span>
            </div>
          </div>
          <h3 class="text-sm font-semibold text-tierra-800 mb-1">{{ addon.nombre }}</h3>
          <p class="text-xs text-gray-500 mb-2">{{ addon.descripcion }}</p>
          <p class="text-sm font-semibold text-dorado-700">
            + {{ formatCOP(addon.precio_cop) }} <span class="font-normal text-gray-400">/ persona</span>
          </p>
        </button>
      </div>
    </div>

    <!-- Resumen de add-ons seleccionados -->
    <div v-if="bookingStore.addOns.length > 0" class="bg-tierra-50/40 border border-tierra-100 rounded-xl p-4 text-sm">
      <p class="font-medium text-tierra-800 mb-2">Experiencias seleccionadas:</p>
      <ul class="space-y-1">
        <li v-for="a in bookingStore.addOns" :key="a.id" class="flex justify-between text-gray-700">
          <span>{{ a.nombre }}</span>
          <span class="font-medium">{{ formatCOP(a.precio_cop) }}</span>
        </li>
      </ul>
    </div>

    <!-- Acciones -->
    <div class="flex flex-col sm:flex-row gap-3 pt-2">
      <button
        type="button"
        class="sm:w-auto order-last sm:order-first px-5 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
        @click="navigateTo('/reservar')"
      >
        ← Volver
      </button>
      <BaseButton class="flex-1 sm:flex-none sm:min-w-[200px]" @click="continuar">
        Continuar →
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'booking' })
useSeoMeta({ title: 'Elige tu experiencia — Hacienda La Carmelita' })

const bookingStore = useBookingStore()

// Guard: si no hay fechas, redirigir al inicio del flujo
onMounted(async () => {
  if (!bookingStore.fechaCheckin || !bookingStore.fechaCheckout) {
    await navigateTo('/reservar')
  }
})

// ─── Add-ons disponibles ───────────────────────────────────────────────────────
const addonsDisponibles = [
  {
    id: 'addon-cabalgata',
    nombre: 'Cabalgata al amanecer',
    descripcion: 'Recorre los senderos de la hacienda a caballo mientras el sol sale sobre los cafetales.',
    precio_cop: 80000,
    cantidad: 1,
    emoji: '🐴',
  },
  {
    id: 'addon-cena',
    nombre: 'Cena gourmet a la leña',
    descripcion: 'Experiencia culinaria bajo las estrellas con productos locales y fogón de leña.',
    precio_cop: 65000,
    cantidad: 1,
    emoji: '🍽️',
  },
  {
    id: 'addon-tour',
    nombre: 'Tour arrocero guiado',
    descripcion: 'Conoce el proceso del cultivo de arroz y la historia agrícola de la región.',
    precio_cop: 45000,
    cantidad: 1,
    emoji: '🌾',
  },
]

// ─── Helpers ──────────────────────────────────────────────────────────────────
const estaSeleccionado = (id: string) =>
  bookingStore.addOns.some((a) => a.id === id)

const formatCOP = (valor: number) =>
  `COP ${valor.toLocaleString('es-CO', { minimumFractionDigits: 0 })}`

const fechaFormateada = (fecha: string | null) => {
  if (!fecha) return '—'
  const [y, m, d] = fecha.split('-')
  const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
  return `${d} ${meses[parseInt(m) - 1]}. ${y}`
}

// ─── Continuar ────────────────────────────────────────────────────────────────
const continuar = async () => {
  bookingStore.setSKU({ id: 'base', nombre: 'Hacienda Completa', precio_cop: 0, precio_usd: 0 })
  await navigateTo('/reservar/datos')
}
</script>
