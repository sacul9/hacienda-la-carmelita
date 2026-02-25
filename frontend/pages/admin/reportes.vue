<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-display font-bold text-tierra-900">Reportes</h1>
      <p class="text-gray-500 mt-1 text-sm">Análisis de reservas e ingresos por período.</p>
    </div>

    <!-- Filtros de período -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
      <h2 class="text-sm font-semibold text-gray-700 mb-4">Período de análisis</h2>
      <div class="flex flex-wrap items-end gap-4">
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">Desde</label>
          <input
            v-model="desde"
            type="date"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tierra-300"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">Hasta</label>
          <input
            v-model="hasta"
            type="date"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tierra-300"
          />
        </div>
        <button
          :disabled="loading"
          class="px-5 py-2 bg-tierra-700 text-white rounded-lg text-sm font-medium hover:bg-tierra-800 transition-colors disabled:opacity-50"
          @click="generar"
        >
          {{ loading ? 'Generando…' : 'Generar reporte' }}
        </button>
        <button
          v-if="data"
          class="px-5 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          @click="exportarCSV"
        >
          Exportar CSV
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
      <p class="text-red-700 font-medium">{{ error }}</p>
      <button
        class="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm"
        @click="generar"
      >
        Reintentar
      </button>
    </div>

    <!-- Loading skeleton -->
    <template v-if="loading">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 animate-pulse">
          <div class="h-4 w-20 bg-gray-200 rounded mb-3" />
          <div class="h-8 w-16 bg-gray-100 rounded" />
        </div>
      </div>
    </template>

    <!-- Resultados -->
    <template v-else-if="data">
      <!-- KPI Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <p class="text-xs text-gray-500 mb-1">Total reservas</p>
          <p class="text-3xl font-bold text-tierra-800">{{ data.total_reservas }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <p class="text-xs text-gray-500 mb-1">Confirmadas</p>
          <p class="text-3xl font-bold text-green-700">{{ data.reservas_confirmadas }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <p class="text-xs text-gray-500 mb-1">Canceladas</p>
          <p class="text-3xl font-bold text-red-600">{{ data.reservas_canceladas }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <p class="text-xs text-gray-500 mb-1">Tasa cancelación</p>
          <p class="text-3xl font-bold text-amber-700">{{ data.tasa_cancelacion }}%</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <p class="text-xs text-gray-500 mb-1">Ingresos totales</p>
          <p class="text-2xl font-bold text-green-700">{{ formatCOP(data.ingresos_totales) }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <p class="text-xs text-gray-500 mb-1">Noches vendidas</p>
          <p class="text-2xl font-bold text-tierra-800">{{ data.noches_totales }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <p class="text-xs text-gray-500 mb-1">Ingreso promedio / noche</p>
          <p class="text-2xl font-bold text-tierra-800">{{ formatCOP(data.ingreso_promedio_noche) }}</p>
        </div>
      </div>

      <!-- Distribución por estado -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <h2 class="text-sm font-semibold text-gray-800 mb-4">Distribución por estado</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <div
            v-for="(count, estado) in data.reservas_por_estado"
            :key="estado"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-xl"
          >
            <div class="flex items-center gap-2">
              <span :class="estadoBadgeClass(String(estado))" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
                {{ estado }}
              </span>
            </div>
            <span class="text-sm font-bold text-gray-800">{{ count }}</span>
          </div>
        </div>
      </div>

      <!-- Tabla detalle -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-gray-800">
            Detalle de reservas
            <span class="ml-2 text-xs text-gray-400 font-normal">({{ data.reservas_detalle.length }})</span>
          </h2>
        </div>

        <div v-if="data.reservas_detalle.length === 0" class="py-12 text-center text-gray-400 text-sm">
          No hay reservas en este período.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-50 bg-gray-50">
                <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Código</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Huésped</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">Fechas</th>
                <th class="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Noches</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Estado</th>
                <th class="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Monto</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr
                v-for="r in data.reservas_detalle"
                :key="r.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-5 py-3 font-mono text-xs text-tierra-700 font-semibold whitespace-nowrap">{{ r.codigo }}</td>
                <td class="px-4 py-3 text-gray-800 whitespace-nowrap">{{ r.huesped_nombre }}</td>
                <td class="px-4 py-3 text-gray-600 text-xs whitespace-nowrap">
                  {{ formatFecha(r.fecha_checkin) }}
                  <span class="text-gray-300 mx-1">→</span>
                  {{ formatFecha(r.fecha_checkout) }}
                </td>
                <td class="px-4 py-3 text-center text-gray-700">{{ r.noches }}</td>
                <td class="px-4 py-3">
                  <span :class="estadoBadgeClass(r.estado)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium whitespace-nowrap">
                    {{ r.estado }}
                  </span>
                </td>
                <td class="px-5 py-3 text-right font-medium text-gray-800 whitespace-nowrap">
                  {{ formatCOP(r.precio_total_cop) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { ReporteData } from '~/composables/useAdmin'

definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Reportes — Hacienda La Carmelita' })

const { fetchReportes } = useAdmin()

// ─── Estado ──────────────────────────────────────────────────────────────────
const hoy = new Date()
const hace30 = new Date(hoy)
hace30.setDate(hace30.getDate() - 30)

const desde = ref(hace30.toISOString().split('T')[0])
const hasta = ref(hoy.toISOString().split('T')[0])
const loading = ref(false)
const error = ref<string | null>(null)
const data = ref<ReporteData | null>(null)

// ─── Acciones ─────────────────────────────────────────────────────────────────
const generar = async () => {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchReportes({ desde: desde.value, hasta: hasta.value })
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Error al generar reporte'
  } finally {
    loading.value = false
  }
}

const exportarCSV = () => {
  if (!data.value) return
  const headers = ['Código', 'Huésped', 'Email', 'Check-in', 'Check-out', 'Noches', 'Estado', 'Monto COP']
  const rows = data.value.reservas_detalle.map(r => [
    r.codigo,
    `"${r.huesped_nombre}"`,
    r.huesped_email,
    r.fecha_checkin,
    r.fecha_checkout,
    r.noches,
    r.estado,
    r.precio_total_cop,
  ])
  const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `reporte-reservas-${desde.value}-al-${hasta.value}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const formatCOP = (v: number) =>
  `COP ${v.toLocaleString('es-CO', { minimumFractionDigits: 0 })}`

const formatFecha = (iso: string) => {
  const clean = iso.split('T')[0]
  const [y, m, d] = clean.split('-')
  const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
  return `${d} ${meses[parseInt(m) - 1]}. ${y}`
}

const estadoBadgeClass = (estado: string): string => {
  const map: Record<string, string> = {
    confirmada: 'bg-green-100 text-green-800',
    pendiente: 'bg-amber-100 text-amber-800',
    otp_pendiente: 'bg-amber-100 text-amber-800',
    pago_pendiente: 'bg-amber-100 text-amber-800',
    cancelada: 'bg-red-100 text-red-800',
    noshow: 'bg-red-100 text-red-800',
    checkin: 'bg-blue-100 text-blue-800',
    checkout: 'bg-blue-100 text-blue-800',
  }
  return map[estado] ?? 'bg-gray-100 text-gray-700'
}

onMounted(generar)
</script>
