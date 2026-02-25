<template>
  <div class="otp-container max-w-md mx-auto">

    <!-- Paso 1: Selección de canal -->
    <div v-if="paso === 'canal'" class="space-y-6">
      <div class="text-center">
        <div class="text-4xl mb-3">🔐</div>
        <h3 class="text-lg font-semibold font-display text-gray-900">Verifica tu identidad</h3>
        <p class="text-sm text-gray-500 mt-1">¿Por dónde prefieres recibir tu código?</p>
      </div>

      <div class="grid grid-cols-3 gap-3">
        <button
          v-for="c in canalesDisponibles"
          :key="c.value"
          :class="[
            'flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200',
            canalSeleccionado === c.value
              ? 'border-tierra-800 bg-tierra-50 text-tierra-800 shadow-sm'
              : 'border-gray-200 hover:border-tierra-300 text-gray-600',
          ]"
          @click="canalSeleccionado = c.value"
        >
          <span class="text-2xl">{{ c.icon }}</span>
          <span class="text-xs font-medium">{{ c.label }}</span>
          <span class="text-xs text-gray-400 truncate w-full text-center">
            {{ c.value === 'email' ? enmascarar(email, 'email') : enmascarar(telefono, 'tel') }}
          </span>
        </button>
      </div>

      <p v-if="errorEnvio" class="text-sm text-red-600 text-center bg-red-50 rounded-lg p-3">{{ errorEnvio }}</p>

      <BaseButton class="w-full" :loading="enviando" :disabled="!canalSeleccionado || enviando" @click="enviarCodigo">
        {{ enviando ? 'Enviando...' : 'Enviar código' }}
      </BaseButton>
    </div>

    <!-- Paso 2: Ingreso del código -->
    <div v-else-if="paso === 'codigo'" class="space-y-6">
      <div class="text-center">
        <div class="text-4xl mb-3">{{ canalSeleccionado === 'email' ? '📧' : canalSeleccionado === 'sms' ? '📱' : '💬' }}</div>
        <h3 class="text-lg font-semibold font-display text-gray-900">Ingresa tu código</h3>
        <p class="text-sm text-gray-500 mt-1">Enviado a <strong>{{ destinoEnmascarado }}</strong></p>
      </div>

      <!-- 6 inputs numéricos -->
      <div class="flex justify-center gap-2">
        <input
          v-for="i in 6"
          :key="i"
          :ref="(el) => setInputRef(el as HTMLInputElement, i - 1)"
          v-model="digitos[i - 1]"
          type="text"
          inputmode="numeric"
          pattern="[0-9]*"
          maxlength="1"
          autocomplete="one-time-code"
          :class="['otp-input', digitos[i-1] ? 'otp-input-filled' : '', errorVerificacion ? 'border-red-400 bg-red-50' : '']"
          @input="handleInput(i - 1, $event)"
          @keydown="handleKeydown(i - 1, $event)"
          @paste.prevent="handlePaste($event)"
          @focus="($event.target as HTMLInputElement).select()"
        />
      </div>

      <!-- Timer -->
      <div class="text-center">
        <span :class="['inline-flex items-center gap-1 text-sm px-3 py-1 rounded-full', timerSeconds > 60 ? 'text-gray-500 bg-gray-100' : timerSeconds > 30 ? 'text-yellow-700 bg-yellow-50' : 'text-red-600 bg-red-50']">
          ⏱ Expira en {{ timerTexto }}
        </span>
      </div>

      <p v-if="errorVerificacion" class="text-sm text-red-600 text-center bg-red-50 rounded-lg p-3">{{ errorVerificacion }}</p>

      <div v-if="verificando" class="text-center text-sm text-tierra-700">
        <span class="inline-block animate-spin mr-2">⟳</span> Verificando...
      </div>

      <!-- Reenviar -->
      <div class="text-center space-y-2">
        <button
          :disabled="segundosReenvio > 0 || enviando"
          :class="['text-sm transition-colors', segundosReenvio > 0 ? 'text-gray-400 cursor-not-allowed' : 'text-tierra-700 hover:text-tierra-900 underline']"
          @click="reenviarCodigo"
        >
          {{ segundosReenvio > 0 ? `Reenviar en ${segundosReenvio}s` : (enviando ? 'Enviando...' : '¿No llegó? Reenviar código') }}
        </button>
        <br>
        <button class="text-xs text-gray-400 hover:text-gray-600 transition-colors" @click="volverACanal">
          Cambiar método de verificación
        </button>
      </div>
    </div>

    <!-- Paso 3: Éxito -->
    <div v-else-if="paso === 'exito'" class="text-center space-y-4 py-4">
      <div class="text-5xl">✅</div>
      <h3 class="text-lg font-semibold font-display text-tierra-800">¡Identidad verificada!</h3>
      <p class="text-sm text-gray-500">Continuando con tu reserva...</p>
    </div>

  </div>
</template>

<script setup lang="ts">
interface Props {
  email?: string
  telefono?: string
  usuarioId?: string
  proposito?: 'registro' | 'reserva' | 'login' | 'pago'
}

const props = withDefaults(defineProps<Props>(), { proposito: 'reserva' })

const emit = defineEmits<{
  verificado: [token: string]
  error: [mensaje: string]
}>()

const { enviarOTP, verificarOTP } = useOTP()

const paso = ref<'canal' | 'codigo' | 'exito'>('canal')
const canalSeleccionado = ref<'email' | 'sms' | 'whatsapp' | null>(null)
const enviando = ref(false)
const verificando = ref(false)
const errorEnvio = ref('')
const errorVerificacion = ref('')
const otpId = ref('')
const digitos = ref<string[]>(Array(6).fill(''))
const inputRefs = ref<(HTMLInputElement | null)[]>(Array(6).fill(null))
const timerSeconds = ref(600)
const segundosReenvio = ref(60)
let timerInterval: ReturnType<typeof setInterval> | null = null
let reenvioInterval: ReturnType<typeof setInterval> | null = null

const canalesDisponibles = computed(() => {
  const c = []
  if (props.email) c.push({ value: 'email' as const, label: 'Email', icon: '📧' })
  if (props.telefono) {
    c.push({ value: 'sms' as const, label: 'SMS', icon: '📱' })
    c.push({ value: 'whatsapp' as const, label: 'WhatsApp', icon: '💬' })
  }
  return c.length ? c : [{ value: 'email' as const, label: 'Email', icon: '📧' }]
})

const destinoEnmascarado = computed(() =>
  canalSeleccionado.value === 'email' ? enmascarar(props.email ?? '', 'email') : enmascarar(props.telefono ?? '', 'tel')
)
const timerTexto = computed(() => `${Math.floor(timerSeconds.value / 60)}:${(timerSeconds.value % 60).toString().padStart(2, '0')}`)

const enmascarar = (v: string, tipo: 'email' | 'tel') => {
  if (!v) return ''
  if (tipo === 'email') { const [u, d] = v.split('@'); return u ? `${u.slice(0,2)}***@${d}` : v }
  return `***${v.slice(-4)}`
}

const setInputRef = (el: HTMLInputElement | null, idx: number) => { inputRefs.value[idx] = el }

const handleInput = (idx: number, event: Event) => {
  const val = (event.target as HTMLInputElement).value.replace(/\D/g,'').slice(-1)
  digitos.value[idx] = val
  errorVerificacion.value = ''
  if (val && idx < 5) nextTick(() => inputRefs.value[idx + 1]?.focus())
  if (digitos.value.every(d => d !== '')) verificarCodigo()
}

const handleKeydown = (idx: number, e: KeyboardEvent) => {
  if (e.key === 'Backspace' && !digitos.value[idx] && idx > 0) nextTick(() => inputRefs.value[idx - 1]?.focus())
  if (e.key === 'ArrowLeft' && idx > 0) inputRefs.value[idx - 1]?.focus()
  if (e.key === 'ArrowRight' && idx < 5) inputRefs.value[idx + 1]?.focus()
}

const handlePaste = (e: ClipboardEvent) => {
  const nums = (e.clipboardData?.getData('text') ?? '').replace(/\D/g,'').slice(0,6)
  if (nums) {
    nums.split('').forEach((d, i) => { digitos.value[i] = d })
    nextTick(() => { inputRefs.value[Math.min(nums.length-1,5)]?.focus(); if (nums.length === 6) verificarCodigo() })
  }
}

const iniciarTimer = () => {
  timerSeconds.value = 600
  if (timerInterval) clearInterval(timerInterval)
  timerInterval = setInterval(() => { timerSeconds.value--; if (timerSeconds.value <= 0) { clearInterval(timerInterval!); errorVerificacion.value = 'El código ha expirado. Solicita uno nuevo.' } }, 1000)
}

const iniciarReenvioTimer = () => {
  segundosReenvio.value = 60
  if (reenvioInterval) clearInterval(reenvioInterval)
  reenvioInterval = setInterval(() => { segundosReenvio.value--; if (segundosReenvio.value <= 0) clearInterval(reenvioInterval!) }, 1000)
}

const enviarCodigo = async () => {
  if (!canalSeleccionado.value || !props.usuarioId) return
  enviando.value = true; errorEnvio.value = ''
  const destino = canalSeleccionado.value === 'email' ? props.email! : props.telefono!
  try {
    const result = await enviarOTP({ destino, canal: canalSeleccionado.value, proposito: props.proposito, usuarioId: props.usuarioId })
    otpId.value = result.otp_id
    paso.value = 'codigo'
    iniciarTimer(); iniciarReenvioTimer()
    nextTick(() => inputRefs.value[0]?.focus())
  } catch (e: any) {
    errorEnvio.value = e?.data?.detail ?? 'Error al enviar el código.'
    emit('error', errorEnvio.value)
  } finally { enviando.value = false }
}

const verificarCodigo = async () => {
  if (verificando.value) return
  const codigo = digitos.value.join('')
  if (codigo.length < 6) return
  verificando.value = true; errorVerificacion.value = ''
  try {
    const result = await verificarOTP({ otpId: otpId.value, codigo })
    if (result.verificado) {
      if (timerInterval) clearInterval(timerInterval)
      paso.value = 'exito'
      setTimeout(() => emit('verificado', result.token ?? ''), 800)
    }
  } catch (e: any) {
    errorVerificacion.value = e?.data?.detail ?? 'Código incorrecto. Intenta de nuevo.'
    digitos.value = Array(6).fill('')
    nextTick(() => inputRefs.value[0]?.focus())
    emit('error', errorVerificacion.value)
  } finally { verificando.value = false }
}

const reenviarCodigo = async () => {
  if (segundosReenvio.value > 0) return
  digitos.value = Array(6).fill(''); errorVerificacion.value = ''
  await enviarCodigo()
}

const volverACanal = () => {
  if (timerInterval) clearInterval(timerInterval)
  if (reenvioInterval) clearInterval(reenvioInterval)
  paso.value = 'canal'; digitos.value = Array(6).fill('')
  errorEnvio.value = ''; errorVerificacion.value = ''
}

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
  if (reenvioInterval) clearInterval(reenvioInterval)
})
</script>
