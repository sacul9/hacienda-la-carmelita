/**
 * Composable del chat IA — Sprint 6
 * Asistente virtual "Carmelita" para huéspedes.
 */

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export const useChat = () => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Mensaje de bienvenida inicial
  const mensajeBienvenida: ChatMessage = {
    role: 'assistant',
    content: '¡Hola! Soy Carmelita, tu asistente virtual 🌿 ¿En qué puedo ayudarte hoy? Puedo responder preguntas sobre la hacienda, servicios, tarifas y más.',
    timestamp: new Date(),
  }

  const inicializar = () => {
    if (messages.value.length === 0) {
      messages.value = [mensajeBienvenida]
    }
  }

  const enviarMensaje = async (texto: string): Promise<void> => {
    if (!texto.trim() || loading.value) return

    // Añadir mensaje del usuario
    messages.value.push({
      role: 'user',
      content: texto.trim(),
      timestamp: new Date(),
    })

    loading.value = true
    error.value = null

    // Construir historial para la API (sin el mensaje de bienvenida artificial)
    const historialAPI = messages.value
      .filter(m => !(m.role === 'assistant' && m === mensajeBienvenida))
      .slice(-20) // últimos 20 mensajes
      .slice(0, -1) // excluir el último (que es el que acabamos de añadir)
      .map(m => ({ role: m.role, content: m.content }))

    try {
      const headers: Record<string, string> = {}
      if (authStore.token) {
        headers.Authorization = `Bearer ${authStore.token}`
      }

      const response = await $fetch<{ respuesta: string }>(`${config.public.apiBase}/chat/mensaje`, {
        method: 'POST',
        headers,
        body: {
          mensaje: texto.trim(),
          historial: historialAPI,
        },
      })

      messages.value.push({
        role: 'assistant',
        content: response.respuesta,
        timestamp: new Date(),
      })
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al conectar con el asistente'
      messages.value.push({
        role: 'assistant',
        content: 'Lo siento, tuve un problema técnico. Puedes contactarnos directamente por WhatsApp 💬',
        timestamp: new Date(),
      })
    } finally {
      loading.value = false
    }
  }

  const limpiarChat = () => {
    messages.value = [mensajeBienvenida]
    error.value = null
  }

  return {
    messages: readonly(messages),
    loading: readonly(loading),
    error: readonly(error),
    inicializar,
    enviarMensaje,
    limpiarChat,
  }
}
