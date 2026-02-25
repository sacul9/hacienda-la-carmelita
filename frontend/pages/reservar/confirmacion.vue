<template>
  <div class="max-w-lg mx-auto py-8 px-4 space-y-6">
    <!-- Icono de celebración -->
    <div class="text-center">
      <div class="text-6xl mb-4">🎉</div>
      <h1 class="text-3xl font-display font-bold text-tierra-800">
        ¡Tu reserva está confirmada!
      </h1>
      <p class="text-gray-500 mt-2 text-sm">
        Gracias por elegir Hacienda La Carmelita. Estamos emocionados de recibirte.
      </p>
    </div>

    <!-- Caja del código de reserva -->
    <div class="bg-tierra-50 border-2 border-tierra-700 rounded-2xl p-6 text-center my-6">
      <p class="text-xs text-tierra-600 uppercase tracking-widest mb-2">Código de reserva</p>
      <p class="font-display text-3xl font-bold text-tierra-800 tracking-wider">
        {{ bookingStore.codigoReserva }}
      </p>
    </div>

    <!-- Detalle de la reserva -->
    <BaseCard class="p-6">
      <h2 class="text-base font-semibold text-tierra-800 mb-4">Detalle de la reserva</h2>
      <div class="space-y-3 text-sm">
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
        <hr class="border-gray-100" />
        <div class="flex justify-between font-semibold text-tierra-800">
          <span>Total pagado</span>
          <span>{{ formatCOP(bookingStore.precioTotal) }}</span>
        </div>
      </div>
    </BaseCard>

    <!-- Aviso de email -->
    <p class="text-center text-sm text-gray-600">
      Recibirás un email de confirmación en
      <strong class="text-tierra-700">{{ bookingStore.huesped?.email ?? '' }}</strong>
    </p>

    <!-- CTAs -->
    <div class="space-y-3">
      <!-- WhatsApp -->
      <a
        :href="whatsappUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="w-full inline-flex items-center justify-center gap-2 bg-tierra-800 hover:bg-tierra-700 text-white font-medium rounded-lg px-6 py-3 text-sm transition-all duration-200"
      >
        <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
        </svg>
        Contactar por WhatsApp
      </a>

      <!-- Volver al inicio -->
      <BaseButton
        variant="outline"
        class="w-full"
        @click="volverAlInicio"
      >
        Volver al inicio
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'booking' })
useSeoMeta({ title: 'Reserva confirmada — Hacienda La Carmelita' })

const bookingStore = useBookingStore()

// Guard: si no hay código de reserva, volver al inicio del flujo
onMounted(async () => {
  if (!bookingStore.codigoReserva) {
    await navigateTo('/reservar')
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

// ─── WhatsApp URL con código de reserva ───────────────────────────────────────
const whatsappUrl = computed(() => {
  const codigo = bookingStore.codigoReserva ?? ''
  const texto = encodeURIComponent(`Hola, mi reserva es ${codigo}`)
  return `https://wa.me/573001234567?text=${texto}`
})

// ─── Volver al inicio y limpiar el store ─────────────────────────────────────
const volverAlInicio = async () => {
  bookingStore.resetBooking()
  await navigateTo('/')
}
</script>
