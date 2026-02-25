/**
 * Composable del panel admin — Sprint 4
 * Conectado a los endpoints /admin/* del backend.
 */

// ── Tipos de respuesta ───────────────────────────────────────────────────────

export interface ReservaAdminItem {
  id: string
  codigo: string
  estado: string
  fecha_checkin: string
  fecha_checkout: string
  noches: number
  huespedes: number
  precio_total_cop: number
  huesped_nombre: string
  huesped_email: string
  created_at: string
}

export interface DashboardData {
  reservas_mes: number
  ingresos_mes: number
  reservas_pendientes: number
  proximas_llegadas: number
  ocupacion_pct: number
  ultimas_reservas: ReservaAdminItem[]
}

export interface ReservasListData {
  items: ReservaAdminItem[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface CalendarioEvento {
  tipo: 'reserva' | 'bloqueo'
  id: string
  codigo?: string
  estado?: string
  motivo?: string
  fecha_inicio: string
  fecha_fin: string
  noches?: number
}

export interface ReporteData {
  periodo_inicio: string
  periodo_fin: string
  total_reservas: number
  reservas_confirmadas: number
  reservas_canceladas: number
  ingresos_totales: number
  noches_totales: number
  tasa_cancelacion: number
  ingreso_promedio_noche: number
  reservas_por_estado: Record<string, number>
  reservas_detalle: ReservaAdminItem[]
}

export interface SyncLogItem {
  id: string
  canal: string
  estado: 'ok' | 'error' | 'en_progreso'
  reservas_importadas: number
  reservas_ya_existian: number
  conflictos_detectados: number
  mensaje_error: string | null
  duracion_ms: number | null
  iniciado_por: string
  created_at: string
}

export interface SyncEstado {
  logs: SyncLogItem[]
  ultima_sync: string | null
  minutos_desde_ultima_sync: number | null
  estado_actual: 'ok' | 'error' | 'sin_datos' | 'alerta'
  total_importadas_hoy: number
  conflictos_pendientes: number
}

// ── Composable ───────────────────────────────────────────────────────────────

export const useAdmin = () => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const _headers = computed(() => {
    const token = authStore.token
    return token ? { Authorization: `Bearer ${token}` } : {}
  })

  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchDashboard = async (): Promise<DashboardData> => {
    loading.value = true
    error.value = null
    try {
      return await $fetch<DashboardData>(`${config.public.apiBase}/admin/dashboard`, {
        headers: _headers.value,
      })
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al cargar el dashboard'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchReservas = async (params: {
    estado?: string
    page?: number
    limit?: number
  } = {}): Promise<ReservasListData> => {
    loading.value = true
    error.value = null
    try {
      const query: Record<string, any> = { page: params.page ?? 1, limit: params.limit ?? 20 }
      if (params.estado) query.estado = params.estado
      return await $fetch<ReservasListData>(`${config.public.apiBase}/admin/reservas`, {
        headers: _headers.value,
        params: query,
      })
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al cargar reservas'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchCalendario = async (mes?: string): Promise<{
    mes: string
    dias: number
    eventos: CalendarioEvento[]
  }> => {
    loading.value = true
    error.value = null
    try {
      const params = mes ? { mes } : {}
      return await $fetch(`${config.public.apiBase}/admin/calendario`, {
        headers: _headers.value,
        params,
      })
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al cargar calendario'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchReportes = async (params: { desde?: string; hasta?: string } = {}): Promise<ReporteData> => {
    loading.value = true
    error.value = null
    try {
      const query: Record<string, any> = {}
      if (params.desde) query.desde = params.desde
      if (params.hasta) query.hasta = params.hasta
      return await $fetch<ReporteData>(`${config.public.apiBase}/admin/reportes`, {
        headers: _headers.value,
        params: query,
      })
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al cargar reportes'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchSync = async (): Promise<SyncEstado> => {
    loading.value = true
    error.value = null
    try {
      return await $fetch<SyncEstado>(`${config.public.apiBase}/admin/sync/estado`, {
        headers: _headers.value,
      })
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al cargar estado de sincronización'
      throw e
    } finally {
      loading.value = false
    }
  }

  const forzarSync = async (): Promise<{ message: string; task_id: string }> => {
    loading.value = true
    error.value = null
    try {
      return await $fetch<{ message: string; task_id: string }>(
        `${config.public.apiBase}/admin/sync/forzar`,
        {
          method: 'POST',
          headers: _headers.value,
        }
      )
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al forzar sincronización'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    loading: readonly(loading),
    error: readonly(error),
    fetchDashboard,
    fetchReservas,
    fetchCalendario,
    fetchReportes,
    fetchSync,
    forzarSync,
  }
}
