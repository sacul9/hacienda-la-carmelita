<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-display font-bold text-tierra-800">Pago seguro</h1>
      <p class="text-gray-500 mt-1 text-sm">Elige tu método de pago y completa tu reserva</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <!-- Panel resumen (izquierda) -->
      <div class="lg:col-span-2 order-first">
        <BaseCard class="p-5 sticky top-6">
          <h2 class="text-base font-semibold text-tierra-800 mb-4">Resumen de tu reserva</h2>

          <!-- Fechas y noches -->
          <div class="space-y-2 text-sm mb-4">
            <div class="flex justify-between">
              <span class="text-gray-500">Check-in</span>
              <span class="font-medium text-gray-800">{{ fechaFormateada(bookingStore.fechaCheckin) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Check-out</span>
              <span class="font-medium text-gray-800">{{ fechaFormateada(bookingStore.fechaCheckout) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Noches</span>
              <span class="font-medium text-gray-800">{{ bookingStore.noches }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Huéspedes</span>
              <span class="font-medium text-gray-800">{{ bookingStore.huesped?.huespedes ?? '—' }}</span>
            </div>
          </div>

          <hr class="border-gray-100 mb-4" />

          <!-- Código de reserva -->
          <div v-if="bookingStore.codigoReserva" class="mb-4">
            <p class="text-xs text-gray-500 mb-1">Código de reserva</p>
            <p class="font-display text-sm font-bold text-tierra-800 tracking-wide">
              {{ bookingStore.codigoReserva }}
            </p>
          </div>

          <hr class="border-gray-100 mb-4" />

          <!-- Total a pagar -->
          <div class="flex justify-between font-semibold text-tierra-800 text-base">
            <span>Total a pagar</span>
            <span>{{ formatCOP(bookingStore.precioTotal) }}</span>
          </div>

          <!-- Seguridad -->
          <div class="mt-4 flex items-center gap-2 text-xs text-gray-400">
            <svg class="h-4 w-4 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <span>Pago 100% seguro. SSL encriptado.</span>
          </div>

          <p class="text-xs text-gray-400 mt-2">
            Cancelación gratuita hasta 7 días antes del check-in.
          </p>
        </BaseCard>
      </div>

      <!-- Panel derecho: selector de pasarela -->
      <div class="lg:col-span-3 order-last">
        <BaseCard class="p-6">
          <h2 class="text-base font-semibold text-tierra-800 mb-5">Selecciona tu método de pago</h2>

          <!-- Tabs de pasarela -->
          <div class="flex rounded-xl overflow-hidden border border-gray-200 mb-6">
            <button
              :class="[
                'flex-1 py-3 px-4 text-sm font-medium transition-all duration-200',
                tabActivo === 'wompi'
                  ? 'bg-tierra-800 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50',
              ]"
              @click="tabActivo = 'wompi'"
            >
              Pago en Colombia (Wompi)
            </button>
            <button
              :class="[
                'flex-1 py-3 px-4 text-sm font-medium transition-all duration-200 border-l border-gray-200',
                tabActivo === 'stripe'
                  ? 'bg-tierra-800 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50',
              ]"
              @click="tabActivo = 'stripe'"
            >
              Pago Internacional (Stripe)
            </button>
          </div>

          <!-- Tab: Wompi -->
          <div v-if="tabActivo === 'wompi'" class="space-y-5">
            <div class="bg-gray-50 rounded-xl p-4 space-y-3">
              <p class="text-sm font-medium text-tierra-800">Métodos de pago disponibles en Colombia</p>
              <div class="grid grid-cols-2 gap-2 text-xs text-gray-600">
                <div class="flex items-center gap-1.5">
                  <span class="text-green-600 font-bold">✓</span>
                  <span>PSE (Débito bancario)</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="text-green-600 font-bold">✓</span>
                  <span>Tarjeta débito / crédito</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="text-green-600 font-bold">✓</span>
                  <span>Nequi</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="text-green-600 font-bold">✓</span>
                  <span>Bancolombia Pay</span>
                </div>
              </div>
              <p class="text-xs text-gray-400 pt-1">
                Serás redirigido a la plataforma segura de Wompi para completar el pago.
              </p>
            </div>

            <!-- Error -->
            <div v-if="errorPago" class="bg-red-50 border border-red-200 rounded-xl p-4">
              <p class="text-sm text-red-700 font-medium mb-1">No se pudo iniciar el pago</p>
              <p class="text-sm text-red-600">{{ errorPago }}</p>
              <button
                class="mt-3 text-sm text-red-700 font-medium underline hover:no-underline"
                @click="errorPago = null"
              >
                Volver a intentarlo
              </button>
            </div>

            <!-- Botón pago Wompi -->
            <BaseButton
              class="w-full"
              size="lg"
              :loading="iniciando"
              :disabled="iniciando"
              @click="pagarConWompi"
            >
              <span v-if="iniciando" class="flex items-center gap-2">
                <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Iniciando pago…
              </span>
              <span v-else>
                Pagar {{ formatCOP(bookingStore.precioTotal) }}
              </span>
            </BaseButton>

            <p class="text-center text-xs text-gray-400">
              Al continuar, aceptas las condiciones de pago y la política de cancelación.
            </p>
          </div>

          <!-- Tab: Stripe -->
          <div v-else-if="tabActivo === 'stripe'" class="space-y-5">
            <div class="bg-gray-50 rounded-xl p-4 space-y-3">
              <p class="text-sm font-medium text-tierra-800">Pago internacional con Stripe</p>
              <div class="grid grid-cols-3 gap-2 text-xs text-gray-600">
                <div class="flex items-center gap-1.5">
                  <span class="text-blue-600 font-bold">✓</span>
                  <span>Visa</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="text-blue-600 font-bold">✓</span>
                  <span>Mastercard</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="text-blue-600 font-bold">✓</span>
                  <span>American Express</span>
                </div>
              </div>
              <p class="text-xs text-gray-400 pt-1">
                El cobro se realiza en COP. Stripe es la plataforma de pagos internacional líder en seguridad.
              </p>
            </div>

            <div class="bg-amber-50 border border-amber-200 rounded-xl p-4">
              <p class="text-sm text-amber-800 font-medium mb-1">Stripe disponible próximamente</p>
              <p class="text-sm text-amber-700">
                Por ahora, te recomendamos usar Wompi (Colombia) o contactarnos directamente por WhatsApp para coordinar tu pago internacional.
              </p>
            </div>

            <BaseButton
              class="w-full"
              size="lg"
              @click="avisarStripe"
            >
              Pagar con Stripe
            </BaseButton>

            <div class="text-center">
              <a
                :href="whatsappStripe"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-2 text-sm text-tierra-700 font-medium hover:underline"
              >
                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                </svg>
                Contactar por WhatsApp
              </a>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'booking' })
useSeoMeta({ title: 'Pago seguro — Hacienda La Carmelita' })

const bookingStore = useBookingStore()
const { iniciarWompi } = usePago()

const tabActivo = ref<'wompi' | 'stripe'>('wompi')
const iniciando = ref(false)
const errorPago = ref<string | null>(null)

// Guards de navegacion
onMounted(async () => {
  if (!bookingStore.reservaId) {
    await navigateTo('/reservar/datos')
    return
  }
  if (!bookingStore.puedeAvanzarPaso4) {
    await navigateTo('/reservar/verificar')
    return
  }
})

// ─── Helpers ──────────────────────────────────────────────────────────────────
const fechaFormateada = (fecha: string | null) => {
  if (!fecha) return '—'
  const [y, m, d] = fecha.split('-')
  const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
  return `${d} ${meses[parseInt(m) - 1]}. ${y}`
}

const formatCOP = (valor: number) =>
  `COP ${valor.toLocaleString('es-CO', { minimumFractionDigits: 0 })}`

const whatsappStripe = computed(() => {
  const codigo = bookingStore.codigoReserva ?? ''
  const texto = encodeURIComponent(`Hola, quiero pagar internacionalmente mi reserva ${codigo}`)
  return `https://wa.me/573001234567?text=${texto}`
})

// ─── Wompi ────────────────────────────────────────────────────────────────────
const pagarConWompi = async () => {
  if (!bookingStore.reservaId) return
  iniciando.value = true
  errorPago.value = null
  try {
    const resultado = await iniciarWompi(bookingStore.reservaId)
    // Redirigir a la URL de checkout de Wompi
    window.location.href = resultado.checkout_url
  } catch (e: any) {
    errorPago.value = e?.data?.detail ?? 'Error al iniciar el pago. Intenta de nuevo.'
    iniciando.value = false
  }
}

// ─── Stripe (próximamente) ────────────────────────────────────────────────────
const avisarStripe = () => {
  alert('Stripe disponible próximamente. Usa Wompi o contáctanos.')
}
</script>
