<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Header -->
    <div class="bg-white border-b border-gray-100 shadow-sm px-4 py-3 flex items-center gap-3">
      <div class="w-9 h-9 rounded-full bg-tierra-100 flex items-center justify-center text-lg shrink-0">
        🌿
      </div>
      <div>
        <h1 class="text-sm font-semibold text-tierra-900">Carmelita — Asistente Virtual</h1>
        <p class="text-xs text-gray-400">Hacienda La Carmelita</p>
      </div>
      <div class="ml-auto flex items-center gap-2">
        <span class="flex items-center gap-1 text-xs text-green-600">
          <span class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
          En línea
        </span>
      </div>
    </div>

    <!-- Mensajes -->
    <div
      ref="mensajesRef"
      class="flex-1 overflow-y-auto px-4 py-4 space-y-4 max-w-2xl mx-auto w-full"
    >
      <div
        v-for="(msg, i) in chat.messages.value"
        :key="i"
        :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <!-- Avatar asistente -->
        <div
          v-if="msg.role === 'assistant'"
          class="w-7 h-7 rounded-full bg-tierra-100 flex items-center justify-center text-sm shrink-0 mr-2 mt-1"
        >
          🌿
        </div>

        <div
          :class="[
            'max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed',
            msg.role === 'user'
              ? 'bg-tierra-700 text-white rounded-br-sm'
              : 'bg-white border border-gray-100 shadow-sm text-gray-800 rounded-bl-sm',
          ]"
        >
          <p class="whitespace-pre-wrap">{{ msg.content }}</p>
          <p
            :class="[
              'text-[10px] mt-1 text-right',
              msg.role === 'user' ? 'text-tierra-200' : 'text-gray-400',
            ]"
          >
            {{ formatHora(msg.timestamp) }}
          </p>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="chat.loading.value" class="flex justify-start">
        <div class="w-7 h-7 rounded-full bg-tierra-100 flex items-center justify-center text-sm shrink-0 mr-2 mt-1">
          🌿
        </div>
        <div class="bg-white border border-gray-100 shadow-sm rounded-2xl rounded-bl-sm px-4 py-3">
          <div class="flex gap-1 items-center">
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms" />
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms" />
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms" />
          </div>
        </div>
      </div>
    </div>

    <!-- Sugerencias rápidas (solo al inicio) -->
    <div
      v-if="chat.messages.value.length <= 1"
      class="px-4 pb-2 max-w-2xl mx-auto w-full"
    >
      <div class="flex flex-wrap gap-2">
        <button
          v-for="s in sugerencias"
          :key="s"
          class="px-3 py-1.5 bg-white border border-tierra-200 rounded-full text-xs text-tierra-700 hover:bg-tierra-50 transition-colors"
          @click="enviar(s)"
        >
          {{ s }}
        </button>
      </div>
    </div>

    <!-- Input -->
    <div class="bg-white border-t border-gray-100 px-4 py-3">
      <div class="max-w-2xl mx-auto flex items-end gap-2">
        <textarea
          v-model="inputMensaje"
          rows="1"
          placeholder="Escribe tu pregunta…"
          class="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-tierra-300 max-h-32"
          @keydown.enter.exact.prevent="enviar(inputMensaje)"
          @input="autoResize"
        />
        <button
          :disabled="!inputMensaje.trim() || chat.loading.value"
          :class="[
            'w-10 h-10 rounded-xl flex items-center justify-center transition-colors shrink-0',
            inputMensaje.trim() && !chat.loading.value
              ? 'bg-tierra-700 text-white hover:bg-tierra-800'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed',
          ]"
          @click="enviar(inputMensaje)"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
      <p class="text-center text-xs text-gray-400 mt-2">
        ¿Prefieres hablar con alguien?
        <a :href="whatsappUrl" target="_blank" class="text-tierra-600 hover:underline font-medium">WhatsApp →</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false }) // Chat usa layout propio (fullscreen)
useSeoMeta({ title: 'Chat — Hacienda La Carmelita' })

const chat = useChat()
const mensajesRef = ref<HTMLElement | null>(null)
const inputMensaje = ref('')

const sugerencias = [
  '¿Cuántos huéspedes admite la hacienda?',
  '¿Cuáles son las tarifas?',
  '¿Hay piscina?',
  '¿Cómo cancelo mi reserva?',
]

const whatsappUrl = 'https://wa.me/573001234567?text=Hola,%20quisiera%20m%C3%A1s%20informaci%C3%B3n'

onMounted(() => chat.inicializar())

const enviar = async (texto: string) => {
  if (!texto.trim() || chat.loading.value) return
  inputMensaje.value = ''
  await chat.enviarMensaje(texto)
  nextTick(() => scrollAlFinal())
}

const scrollAlFinal = () => {
  if (mensajesRef.value) {
    mensajesRef.value.scrollTop = mensajesRef.value.scrollHeight
  }
}

const autoResize = (e: Event) => {
  const el = e.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 128) + 'px'
}

const formatHora = (fecha: Date) =>
  fecha.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })

// Scroll al final cuando llegan nuevos mensajes
watch(() => chat.messages.value.length, () => nextTick(scrollAlFinal))
</script>
