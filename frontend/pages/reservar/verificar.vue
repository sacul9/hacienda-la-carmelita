<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-display font-bold text-tierra-800">Verifica tu identidad</h1>
      <p class="text-gray-500 mt-1 text-sm">
        Te enviamos un código de 6 dígitos a
        <strong class="text-tierra-700">{{ destino }}</strong>
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <!-- Resumen lateral -->
      <div class="lg:col-span-2 order-first">
        <BaseCard class="p-5 sticky top-6">
          <h2 class="text-base font-semibold text-tierra-800 mb-4">Resumen de tu reserva</h2>
          <div class="space-y-2 text-sm">
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
              <span class="font-medium text-gray-800">{{ bookingStore.huesped?.huespedes }}</span>
            </div>
          </div>
          <hr class="border-gray-100 my-4" />
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500">Nombre</span>
              <span class="text-gray-800">{{ bookingStore.huesped?.nombre }} {{ bookingStore.huesped?.apellido }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Email</span>
              <span class="text-gray-800 truncate max-w-[140px]">{{ bookingStore.huesped?.email }}</span>
            </div>
          </div>
          <p class="text-xs text-gray-400 mt-4">
            Cancelación gratuita hasta 7 días antes del check-in.
          </p>
        </BaseCard>
      </div>

      <!-- Panel verificación -->
      <div class="lg:col-span-3 order-last">
        <BaseCard class="p-6 space-y-6">

          <!-- Estado: enviando OTP -->
          <div v-if="estado === 'enviando'" class="flex flex-col items-center gap-3 py-8">
            <svg class="animate-spin h-8 w-8 text-tierra-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p class="text-sm text-gray-600">Enviando código de verificación…</p>
          </div>

          <!-- Estado: esperando código -->
          <div v-else-if="estado === 'esperando'" class="space-y-6">
            <div>
              <p class="text-sm text-gray-700 mb-1">
                Ingresa el código de 6 dígitos que enviamos por
                <span class="font-semibold">{{ canal.toUpperCase() }}</span>:
              </p>
              <p class="text-xs text-gray-400">Válido por 10 minutos · Código de uso único</p>
            </div>

            <!-- Input OTP -->
            <div class="flex gap-3 justify-center">
              <input
                v-for="(_, i) in digitos"
                :key="i"
                :ref="(el) => setInputRef(el, i)"
                v-model="digitos[i]"
                type="text"
                inputmode="numeric"
                maxlength="1"
                class="w-12 h-14 text-center text-2xl font-bold rounded-xl border-2 text-tierra-900
                       focus:outline-none focus:ring-2 focus:ring-tierra-700 transition
                       border-gray-200 focus:border-tierra-700"
                :class="{ 'border-red-400': errorOTP }"
                @input="onDigitoInput(i, $event)"
                @keydown.backspace="onBackspace(i)"
                @paste.prevent="onPaste($event)"
              />
            </div>

            <!-- Error -->
            <p v-if="errorOTP" class="text-sm text-red-600 text-center bg-red-50 rounded-lg p-3">
              {{ errorOTP }}
            </p>

            <!-- Botón verificar -->
            <BaseButton
              class="w-full"
              :disabled="codigoCompleto === false || verificando"
              @click="verificar"
            >
              <span v-if="verificando" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Verificando…
              </span>
              <span v-else>Confirmar código →</span>
            </BaseButton>

            <!-- Reenviar -->
            <div class="text-center">
              <button
                v-if="tiempoReenvio > 0"
                disabled
                class="text-sm text-gray-400 cursor-not-allowed"
              >
                Reenviar código en {{ tiempoReenvio }}s
              </button>
              <button
                v-else
                class="text-sm text-tierra-700 font-medium hover:underline"
                :disabled="enviandoReenvio"
                @click="reenviarOTP"
              >
                {{ enviandoReenvio ? 'Reenviando…' : '¿No recibiste el código? Reenviar' }}
              </button>
            </div>
          </div>

          <!-- Estado: creando reserva -->
          <div v-else-if="estado === 'creando'" class="flex flex-col items-center gap-3 py-8">
            <svg class="animate-spin h-8 w-8 text-tierra-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p class="text-sm text-gray-600">Creando tu reserva…</p>
          </div>

          <!-- Estado: error fatal -->
          <div v-else-if="estado === 'error'" class="text-center space-y-4 py-6">
            <div class="text-4xl">⚠️</div>
            <p class="text-gray-700 font-medium">Algo salió mal</p>
            <p class="text-sm text-red-600 bg-red-50 rounded-lg p-3">{{ errorFatal }}</p>
            <BaseButton class="w-full" @click="reintentar">
              Volver a intentarlo
            </BaseButton>
          </div>

        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'booking' })
useSeoMeta({ title: 'Verificación de identidad — Hacienda La Carmelita' })

const bookingStore = useBookingStore()
const { registro } = useAuth()
const { enviarOTP, verificarOTP } = useOTP()
const { crearReserva } = useBooking()

// ─── Estado de la página ────────────────────────────────────────────────────
type Paso = 'enviando' | 'esperando' | 'creando' | 'error'
const estado = ref<Paso>('enviando')
const errorFatal = ref('')

// ─── Canal y destino ────────────────────────────────────────────────────────
const canal = ref<'email' | 'whatsapp'>('email')
const destino = computed(() =>
  canal.value === 'email'
    ? bookingStore.huesped?.email ?? ''
    : bookingStore.huesped?.telefono ?? ''
)

// ─── OTP ID (retornado por el backend) ──────────────────────────────────────
const otpId = ref('')

// ─── Inputs de 6 dígitos ────────────────────────────────────────────────────
const digitos = ref<string[]>(Array(6).fill(''))
const inputRefs = ref<(HTMLInputElement | null)[]>(Array(6).fill(null))
const setInputRef = (el: any, i: number) => { inputRefs.value[i] = el }
const codigoCompleto = computed(() => digitos.value.every((d) => d !== ''))
const codigoString = computed(() => digitos.value.join(''))

const errorOTP = ref('')
const verificando = ref(false)

// ─── Reenvío ────────────────────────────────────────────────────────────────
const tiempoReenvio = ref(60)
const enviandoReenvio = ref(false)
let reenvioTimer: ReturnType<typeof setInterval> | null = null

const iniciarCountdown = () => {
  tiempoReenvio.value = 60
  reenvioTimer = setInterval(() => {
    tiempoReenvio.value--
    if (tiempoReenvio.value <= 0 && reenvioTimer) clearInterval(reenvioTimer)
  }, 1000)
}

onUnmounted(() => { if (reenvioTimer) clearInterval(reenvioTimer) })

// ─── Guard: si no viene de /datos, redirige ──────────────────────────────────
onMounted(async () => {
  if (!bookingStore.puedeAvanzarPaso3) {
    await navigateTo('/reservar/datos')
    return
  }
  await enviarCodigo()
})

// ─── Flujo principal: registro → OTP ────────────────────────────────────────
const enviarCodigo = async () => {
  estado.value = 'enviando'
  errorFatal.value = ''
  try {
    // 1. Registrar (o recuperar) usuario guest en el backend
    const huesped = bookingStore.huesped!
    const usuario = await registro({
      email: huesped.email,
      nombre: huesped.nombre,
      apellido: huesped.apellido,
      telefono: huesped.telefono,
      pais: huesped.pais,
    })

    // 2. Enviar OTP al email del huésped
    const otpResult = await enviarOTP({
      destino: huesped.email,
      canal: 'email',
      proposito: 'reserva',
      usuarioId: usuario.id,
    })
    otpId.value = otpResult.otp_id
    canal.value = 'email'

    estado.value = 'esperando'
    iniciarCountdown()

    // Enfocar primer input
    await nextTick()
    inputRefs.value[0]?.focus()
  } catch (e: any) {
    estado.value = 'error'
    errorFatal.value = e?.data?.detail ?? 'No se pudo enviar el código. Intenta de nuevo.'
  }
}

const reenviarOTP = async () => {
  enviandoReenvio.value = true
  try {
    await enviarCodigo()
    digitos.value = Array(6).fill('')
    errorOTP.value = ''
    await nextTick()
    inputRefs.value[0]?.focus()
  } finally {
    enviandoReenvio.value = false
  }
}

// ─── Verificar código ────────────────────────────────────────────────────────
const verificar = async () => {
  if (!codigoCompleto.value || verificando.value) return
  verificando.value = true
  errorOTP.value = ''
  try {
    const result = await verificarOTP({ otpId: otpId.value, codigo: codigoString.value })
    if (!result.verificado || !result.token) {
      errorOTP.value = 'Código incorrecto. Verifica e intenta de nuevo.'
      return
    }

    // Guardar token OTP en el store
    bookingStore.confirmarOTP(result.token)

    // Crear reserva inmediatamente con el token OTP
    estado.value = 'creando'
    await crearReserva(result.token)

    // Navegar al paso de pago
    await navigateTo('/reservar/pago')
  } catch (e: any) {
    const detail = e?.data?.detail ?? ''
    if (typeof detail === 'string' && detail.toLowerCase().includes('inválido')) {
      estado.value = 'error'
      errorFatal.value = detail
    } else {
      errorOTP.value = detail || 'Código incorrecto o expirado. Intenta de nuevo.'
      estado.value = 'esperando'
    }
  } finally {
    verificando.value = false
  }
}

const reintentar = async () => {
  digitos.value = Array(6).fill('')
  errorOTP.value = ''
  otpId.value = ''
  await enviarCodigo()
}

// ─── Manejo de inputs OTP ────────────────────────────────────────────────────
const onDigitoInput = (i: number, e: Event) => {
  const val = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  digitos.value[i] = val.slice(-1)
  if (val && i < 5) inputRefs.value[i + 1]?.focus()
}

const onBackspace = (i: number) => {
  if (!digitos.value[i] && i > 0) {
    digitos.value[i - 1] = ''
    inputRefs.value[i - 1]?.focus()
  }
}

const onPaste = (e: ClipboardEvent) => {
  const text = e.clipboardData?.getData('text') ?? ''
  const numeros = text.replace(/\D/g, '').slice(0, 6).split('')
  numeros.forEach((n, i) => { if (i < 6) digitos.value[i] = n })
  inputRefs.value[Math.min(numeros.length, 5)]?.focus()
}

// ─── Utilidades ──────────────────────────────────────────────────────────────
const fechaFormateada = (fecha: string | null) => {
  if (!fecha) return '—'
  const [y, m, d] = fecha.split('-')
  const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
  return `${d} ${meses[parseInt(m) - 1]}. ${y}`
}
</script>
