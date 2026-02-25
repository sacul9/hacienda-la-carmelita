<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-display font-bold text-tierra-800">Tus datos</h1>
      <p class="text-gray-500 mt-1 text-sm">Completa la información para tu reserva</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <!-- Panel resumen (izquierda / arriba en mobile) -->
      <div class="lg:col-span-2 order-first">
        <BaseCard class="p-5 sticky top-6">
          <h2 class="text-base font-semibold text-tierra-800 mb-4">Resumen de tu reserva</h2>

          <!-- Fechas -->
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
              <span class="font-medium text-gray-800">{{ form.huespedes }}</span>
            </div>
          </div>

          <hr class="border-gray-100 mb-4" />

          <!-- Precio -->
          <div v-if="loadingPrecio" class="flex items-center gap-2 text-sm text-tierra-700 py-2">
            <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>Calculando precio...</span>
          </div>

          <div v-else-if="precioData" class="space-y-2 text-sm">
            <div
              v-for="item in precioData.desglose"
              :key="item.concepto"
              class="flex justify-between text-gray-600"
            >
              <span>{{ item.concepto }}</span>
              <span>{{ formatCOP(item.monto) }}</span>
            </div>
            <div v-if="precioData.addons_cop > 0" class="flex justify-between text-gray-600">
              <span>Add-ons</span>
              <span>{{ formatCOP(precioData.addons_cop) }}</span>
            </div>
            <hr class="border-gray-100 my-2" />
            <div class="flex justify-between font-semibold text-tierra-800">
              <span>Total</span>
              <span>{{ formatCOP(precioData.total_cop) }}</span>
            </div>
            <div v-if="precioData.total_usd" class="text-right text-xs text-gray-400">
              ≈ USD {{ precioData.total_usd.toLocaleString('en-US', { minimumFractionDigits: 0 }) }}
            </div>
          </div>

          <div v-else-if="errorPrecio" class="text-sm text-red-600 bg-red-50 rounded-lg p-3">
            {{ errorPrecio }}
          </div>

          <p class="text-xs text-gray-400 mt-4">
            Cancelación gratuita hasta 7 días antes del check-in.
          </p>
        </BaseCard>
      </div>

      <!-- Panel formulario (derecha / abajo en mobile) -->
      <div class="lg:col-span-3 order-last">
        <BaseCard class="p-6">
          <h2 class="text-base font-semibold text-tierra-800 mb-5">Información del huésped</h2>

          <form class="space-y-4" @submit.prevent="continuar">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Nombre -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nombre <span class="text-red-500">*</span></label>
                <input
                  v-model="form.nombre"
                  type="text"
                  placeholder="Juan"
                  :class="inputClass(errors.nombre)"
                />
                <p v-if="errors.nombre" class="text-xs text-red-600 mt-1">{{ errors.nombre }}</p>
              </div>

              <!-- Apellido -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Apellido <span class="text-red-500">*</span></label>
                <input
                  v-model="form.apellido"
                  type="text"
                  placeholder="Pérez"
                  :class="inputClass(errors.apellido)"
                />
                <p v-if="errors.apellido" class="text-xs text-red-600 mt-1">{{ errors.apellido }}</p>
              </div>
            </div>

            <!-- Email -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Correo electrónico <span class="text-red-500">*</span></label>
              <input
                v-model="form.email"
                type="email"
                placeholder="juan@ejemplo.com"
                :class="inputClass(errors.email)"
              />
              <p v-if="errors.email" class="text-xs text-red-600 mt-1">{{ errors.email }}</p>
            </div>

            <!-- Teléfono -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono <span class="text-red-500">*</span></label>
              <input
                v-model="form.telefono"
                type="tel"
                placeholder="+57 300 000 0000"
                :class="inputClass(errors.telefono)"
              />
              <p v-if="errors.telefono" class="text-xs text-red-600 mt-1">{{ errors.telefono }}</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- País -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">País</label>
                <input
                  v-model="form.pais"
                  type="text"
                  placeholder="Colombia"
                  :class="inputClass()"
                />
              </div>

              <!-- Huéspedes -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Huéspedes</label>
                <input
                  v-model.number="form.huespedes"
                  type="number"
                  min="1"
                  max="18"
                  :class="inputClass()"
                />
              </div>
            </div>

            <!-- Notas -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Notas adicionales <span class="text-gray-400 font-normal">(opcional)</span>
              </label>
              <textarea
                v-model="form.notas"
                rows="3"
                placeholder="Alergias, necesidades especiales, hora estimada de llegada..."
                class="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-tierra-700 focus:border-transparent transition resize-none"
              />
            </div>

            <!-- CTA -->
            <div class="pt-2">
              <BaseButton type="submit" class="w-full">
                Continuar a verificación →
              </BaseButton>
            </div>
          </form>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'booking' })
useSeoMeta({ title: 'Tus datos — Hacienda La Carmelita' })

const bookingStore = useBookingStore()
const { calcularPrecio } = useBooking()

const loadingPrecio = ref(false)
const errorPrecio = ref('')
const precioData = ref<{
  noches: number
  precio_base_cop: number
  addons_cop: number
  total_cop: number
  total_usd: number | null
  desglose: Array<{ concepto: string; monto: number }>
} | null>(null)

const form = reactive({
  nombre: bookingStore.huesped?.nombre ?? '',
  apellido: bookingStore.huesped?.apellido ?? '',
  email: bookingStore.huesped?.email ?? '',
  telefono: bookingStore.huesped?.telefono ?? '',
  pais: bookingStore.huesped?.pais ?? 'Colombia',
  huespedes: bookingStore.huesped?.huespedes ?? 2,
  notas: bookingStore.huesped?.notas ?? '',
})
const errors = reactive<Record<string, string>>({})

// Guard + cargar precio
onMounted(async () => {
  if (!bookingStore.puedeAvanzarPaso1) {
    await navigateTo('/reservar')
    return
  }
  loadingPrecio.value = true
  errorPrecio.value = ''
  try {
    precioData.value = await calcularPrecio({
      desde: bookingStore.fechaCheckin!,
      hasta: bookingStore.fechaCheckout!,
      huespedes: form.huespedes,
    })
  } catch (e: any) {
    errorPrecio.value = e?.data?.detail ?? 'Error al calcular precio'
  } finally {
    loadingPrecio.value = false
  }
})

const fechaFormateada = (fecha: string | null) => {
  if (!fecha) return '—'
  const [y, m, d] = fecha.split('-')
  const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
  return `${d} ${meses[parseInt(m) - 1]}. ${y}`
}

const formatCOP = (valor: number) =>
  `COP ${valor.toLocaleString('es-CO', { minimumFractionDigits: 0 })}`

const inputClass = (error?: string) => [
  'w-full rounded-xl border bg-white px-4 py-2.5 text-gray-900 text-sm focus:outline-none focus:ring-2 focus:border-transparent transition',
  error
    ? 'border-red-300 focus:ring-red-400'
    : 'border-gray-200 focus:ring-tierra-700',
]

const validar = () => {
  Object.keys(errors).forEach((k) => delete errors[k])
  if (!form.nombre.trim()) errors.nombre = 'Requerido'
  if (!form.apellido.trim()) errors.apellido = 'Requerido'
  if (!form.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errors.email = 'Email inválido'
  if (!form.telefono || form.telefono.replace(/\D/g, '').length < 7) errors.telefono = 'Teléfono inválido'
  return Object.keys(errors).length === 0
}

const continuar = async () => {
  if (!validar()) return
  bookingStore.setHuesped({
    nombre: form.nombre,
    apellido: form.apellido,
    email: form.email,
    telefono: form.telefono,
    pais: form.pais,
    huespedes: form.huespedes,
    notas: form.notas,
  })
  await navigateTo('/reservar/verificar')
}
</script>
