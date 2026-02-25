<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-3xl font-display font-bold text-tierra-800">Reserva tu escapada</h1>
      <p class="text-gray-500 mt-2">Selecciona las fechas de tu estadía en Hacienda La Carmelita</p>
    </div>

    <BaseCard class="p-6 max-w-3xl mx-auto">
      <div class="space-y-6">

        <!-- Calendario de rango -->
        <BookingCalendar
          :checkin="fechaCheckin"
          :checkout="fechaCheckout"
          @update:checkin="fechaCheckin = $event"
          @update:checkout="fechaCheckout = $event"
        />

        <!-- Huéspedes -->
        <div class="border-t border-gray-100 pt-5">
          <label class="block text-sm font-medium text-tierra-800 mb-2">👥 Número de huéspedes</label>
          <div class="flex items-center gap-3">
            <button
              type="button"
              class="w-9 h-9 rounded-full border-2 border-gray-200 flex items-center justify-center text-lg text-tierra-800 hover:border-tierra-600 transition disabled:opacity-30"
              :disabled="huespedes <= 1"
              @click="huespedes = Math.max(1, huespedes - 1)"
            >−</button>
            <span class="w-8 text-center font-semibold text-tierra-800 text-lg">{{ huespedes }}</span>
            <button
              type="button"
              class="w-9 h-9 rounded-full border-2 border-gray-200 flex items-center justify-center text-lg text-tierra-800 hover:border-tierra-600 transition disabled:opacity-30"
              :disabled="huespedes >= 18"
              @click="huespedes = Math.min(18, huespedes + 1)"
            >+</button>
            <span class="text-sm text-gray-400">/ máx. 18 huéspedes</span>
          </div>
        </div>

        <!-- Disponibilidad si el backend responde -->
        <div
          v-if="disponibilidadData && !disponibilidadData.disponible"
          class="flex items-start gap-2 rounded-xl p-3 text-sm bg-red-50 text-red-800 border border-red-200"
        >
          <span class="text-base leading-none mt-0.5">✗</span>
          <span>{{ disponibilidadData.mensaje ?? 'Las fechas seleccionadas no están disponibles. Por favor elige otras fechas.' }}</span>
        </div>

        <!-- Botón continuar -->
        <BaseButton
          :disabled="!puedeAvanzar"
          size="lg"
          class="w-full"
          @click="continuar"
        >
          Continuar →
        </BaseButton>
        <p class="text-xs text-center text-gray-400 -mt-3">
          Mínimo 2 noches · Cancelación gratuita 7 días antes
        </p>

      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'booking' })
useSeoMeta({ title: 'Selecciona fechas — Hacienda La Carmelita' })

const bookingStore = useBookingStore()
const { verificarDisponibilidad } = useBooking()

const fechaCheckin = ref(bookingStore.fechaCheckin ?? '')
const fechaCheckout = ref(bookingStore.fechaCheckout ?? '')
const huespedes = ref(bookingStore.huesped?.huespedes ?? 2)
const disponibilidadData = ref<{ fechas_bloqueadas: string[]; disponible: boolean; mensaje?: string } | null>(null)

const noches = computed(() => {
  if (!fechaCheckin.value || !fechaCheckout.value) return 0
  return Math.round(
    (new Date(fechaCheckout.value).getTime() - new Date(fechaCheckin.value).getTime()) / 86400000
  )
})

// Habilitar Continuar cuando haya ≥ 2 noches seleccionadas
// y el API no haya confirmado explícitamente que no hay disponibilidad
const puedeAvanzar = computed(() =>
  noches.value >= 2 && disponibilidadData.value?.disponible !== false
)

// Verificar disponibilidad en segundo plano (no bloquea el botón si falla)
watch([fechaCheckin, fechaCheckout], async ([ci, co]) => {
  disponibilidadData.value = null
  if (!ci || !co || noches.value < 2) return
  try {
    disponibilidadData.value = await verificarDisponibilidad(ci, co)
  } catch {
    // Backend no disponible — no bloqueamos
  }
})

const continuar = async () => {
  bookingStore.setFechas(fechaCheckin.value, fechaCheckout.value)
  await navigateTo('/reservar/experiencias')
}
</script>
