/**
 * Composable de pagos — Sprint 3
 * Conectado a los endpoints reales del backend: /pagos/wompi/* y /pagos/stripe/*
 */
export const usePago = () => {
  const config = useRuntimeConfig()
  const bookingStore = useBookingStore()

  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Inicia pago con Wompi. Requiere OTP token en el header.
   * Retorna la URL de checkout de Wompi.
   */
  const iniciarWompi = async (reservaId: string): Promise<{
    pago_id: string
    checkout_url: string
    referencia: string
    monto_cop: number
  }> => {
    loading.value = true
    error.value = null
    try {
      return await $fetch(`${config.public.apiBase}/pagos/wompi/iniciar`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${bookingStore.otpToken}` },
        body: { reserva_id: reservaId },
      })
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al iniciar pago con Wompi'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Obtiene el estado de un pago (polling).
   */
  const obtenerEstadoPago = async (pagoId: string): Promise<{
    pago_id: string
    estado: 'pendiente' | 'aprobado' | 'rechazado' | 'reembolsado'
    pasarela: string
    monto: number
    moneda: string
  }> => {
    return await $fetch(`${config.public.apiBase}/pagos/${pagoId}/estado`)
  }

  return {
    loading: readonly(loading),
    error: readonly(error),
    iniciarWompi,
    obtenerEstadoPago,
  }
}
