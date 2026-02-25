/**
 * Composable del motor de reservas — Sprint 1
 * Disponibilidad y precio conectados a la API.
 */
export const useBooking = () => {
  const config = useRuntimeConfig()
  const bookingStore = useBookingStore()

  const loading = ref(false)
  const error = ref<string | null>(null)

  const verificarDisponibilidad = async (desde: string, hasta: string) => {
    loading.value = true
    error.value = null
    try {
      return await $fetch<{ fechas_bloqueadas: string[]; disponible: boolean; mensaje?: string }>(
        `${config.public.apiBase}/disponibilidad`, { params: { desde, hasta } }
      )
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al verificar disponibilidad'
      throw e
    } finally {
      loading.value = false
    }
  }

  const calcularPrecio = async (params: {
    desde: string; hasta: string; huespedes: number; skus?: string[]
  }) => {
    loading.value = true
    error.value = null
    try {
      return await $fetch<{
        noches: number; precio_base_cop: number; addons_cop: number
        total_cop: number; total_usd: number | null
        desglose: Array<{ concepto: string; monto: number }>
      }>(`${config.public.apiBase}/disponibilidad/precio`, {
        params: { desde: params.desde, hasta: params.hasta, huespedes: params.huespedes, skus: params.skus?.join(',') }
      })
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al calcular precio'
      throw e
    } finally {
      loading.value = false
    }
  }

  const crearReserva = async (otpToken: string) => {
    const store = bookingStore
    loading.value = true
    error.value = null
    try {
      const result = await $fetch<{ id: string; codigo: string; estado: string; noches: number; precio_total_cop: number }>(
        `${config.public.apiBase}/reservas`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${otpToken}` },
          body: {
            fecha_checkin: store.fechaCheckin,
            fecha_checkout: store.fechaCheckout,
            huespedes: store.huesped?.huespedes ?? 1,
            sku_id: store.skuSeleccionado?.id,
            addon_ids: store.addOns.map((a: any) => a.id),
            notas_huesped: store.huesped?.notas,
          },
        }
      )
      store.setReserva(result.id, result.codigo)
      return result
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al crear reserva'
      throw e
    } finally {
      loading.value = false
    }
  }

  return { loading: readonly(loading), error: readonly(error), verificarDisponibilidad, calcularPrecio, crearReserva }
}
