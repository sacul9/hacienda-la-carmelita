/**
 * Composable OTP — Sprint 1
 * Conectado a los endpoints reales del backend.
 */
export const useOTP = () => {
  const config = useRuntimeConfig()

  const enviarOTP = async (params: {
    destino: string
    canal: 'email' | 'sms' | 'whatsapp'
    proposito: 'registro' | 'reserva' | 'login' | 'pago'
    usuarioId: string
  }): Promise<{ otp_id: string; canal: string; mensaje: string; expires_en_minutos: number }> => {
    return await $fetch(`${config.public.apiBase}/auth/otp/enviar`, {
      method: 'POST',
      body: {
        destino: params.destino,
        canal: params.canal,
        proposito: params.proposito,
        usuario_id: params.usuarioId,
      },
    })
  }

  const verificarOTP = async (params: {
    otpId: string
    codigo: string
  }): Promise<{ verificado: boolean; mensaje: string; token: string | null }> => {
    return await $fetch(`${config.public.apiBase}/auth/otp/verificar`, {
      method: 'POST',
      body: { otp_id: params.otpId, codigo: params.codigo },
    })
  }

  return { enviarOTP, verificarOTP }
}
