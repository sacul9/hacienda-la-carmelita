<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-display font-bold text-tierra-900">Reservas</h1>
      <p class="text-gray-500 mt-1 text-sm">Gestiona todas las reservas de la hacienda.</p>
    </div>

    <!-- Filtros de estado -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="f in filtros"
        :key="f.value"
        :class="[
          'px-4 py-2 rounded-lg text-sm font-medium transition-colors border',
          filtroEstado === f.value
            ? 'bg-tierra-700 text-white border-tierra-700'
            : 'bg-white text-gray-600 border-gray-200 hover:border-tierra-300 hover:text-tierra-700',
        ]"
        @click="seleccionarFiltro(f.value)"
      >
        {{ f.label }}
      </button>
    </div>

    <!-- Loading skeleton -->
    <template v-if="loading">
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div class="divide-y divide-gray-50">
          <div
            v-for="i in 6"
            :key="i"
            class="px-6 py-4 animate-pulse flex gap-4"
          >
            <div class="h-4 w-24 bg-gray-200 rounded" />
            <div class="h-4 w-32 bg-gray-100 rounded" />
            <div class="h-4 w-40 bg-gray-100 rounded" />
            <div class="h-4 w-28 bg-gray-100 rounded" />
            <div class="h-4 w-20 bg-gray-100 rounded" />
          </div>
        </div>
      </div>
    </template>

    <!-- Error state -->
    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 rounded-2xl p-8 text-center"
    >
      <p class="text-red-700 font-medium">{{ error }}</p>
      <button
        class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors"
        @click="cargar"
      >
        Reintentar
      </button>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="data && data.items.length === 0"
      class="bg-white rounded-2xl border border-gray-100 shadow-sm p-12 text-center"
    >
      <p class="text-4xl mb-3">📭</p>
      <p class="text-gray-500 text-sm">No hay reservas con este filtro.</p>
    </div>

    <!-- Tabla -->
    <template v-else-if="data">
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-100 bg-gray-50">
                <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">Código</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">Huésped</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">Email</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">Fechas</th>
                <th class="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">Noches</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">Estado</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">Monto</th>
                <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">Creada</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr
                v-for="r in data.items"
                :key="r.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-5 py-3 font-mono text-xs text-tierra-700 font-semibold whitespace-nowrap">{{ r.codigo }}</td>
                <td class="px-4 py-3 text-gray-800 whitespace-nowrap">{{ r.huesped_nombre }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ r.huesped_email }}</td>
                <td class="px-4 py-3 text-gray-600 whitespace-nowrap text-xs">
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
                <td class="px-4 py-3 text-right text-gray-800 font-medium whitespace-nowrap">{{ formatCOP(r.precio_total_cop) }}</td>
                <td class="px-5 py-3 text-gray-400 text-xs whitespace-nowrap">{{ formatFecha(r.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Paginación -->
      <div
        v-if="data.pages > 1"
        class="flex items-center justify-between bg-white rounded-2xl border border-gray-100 shadow-sm px-6 py-4"
      >
        <button
          :disabled="paginaActual <= 1"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            paginaActual <= 1
              ? 'text-gray-300 cursor-not-allowed'
              : 'text-tierra-700 hover:bg-tierra-50',
          ]"
          @click="paginaActual > 1 && irAPagina(paginaActual - 1)"
        >
          ← Anterior
        </button>

        <span class="text-sm text-gray-500">
          Página <span class="font-semibold text-gray-800">{{ paginaActual }}</span> de
          <span class="font-semibold text-gray-800">{{ data.pages }}</span>
          <span class="ml-2 text-gray-400">({{ data.total }} reservas)</span>
        </span>

        <button
          :disabled="paginaActual >= data.pages"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            paginaActual >= data.pages
              ? 'text-gray-300 cursor-not-allowed'
              : 'text-tierra-700 hover:bg-tierra-50',
          ]"
          @click="paginaActual < data.pages && irAPagina(paginaActual + 1)"
        >
          Siguiente →
        </button>
      </div>

      <!-- Info de página cuando solo hay una -->
      <div
        v-else-if="data.total > 0"
        class="text-center text-xs text-gray-400"
      >
        {{ data.total }} reserva{{ data.total !== 1 ? 's' : '' }} en total
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { ReservasListData } from '~/composables/useAdmin'

definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Reservas — Hacienda La Carmelita' })

const { fetchReservas } = useAdmin()

const filtros = [
  { label: 'Todas', value: '' },
  { label: 'Pendientes', value: 'pendiente' },
  { label: 'Confirmadas', value: 'confirmada' },
  { label: 'Check-in', value: 'checkin' },
  { label: 'Check-out', value: 'checkout' },
  { label: 'Canceladas', value: 'cancelada' },
]

const filtroEstado = ref('')
const paginaActual = ref(1)
const loading = ref(true)
const error = ref<string | null>(null)
const data = ref<ReservasListData | null>(null)

const cargar = async () => {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchReservas({
      estado: filtroEstado.value || undefined,
      page: paginaActual.value,
      limit: 20,
    })
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Error al cargar reservas'
  } finally {
    loading.value = false
  }
}

const seleccionarFiltro = (valor: string) => {
  filtroEstado.value = valor
}

const irAPagina = (pagina: number) => {
  paginaActual.value = pagina
}

onMounted(cargar)

watch(filtroEstado, () => {
  paginaActual.value = 1
  cargar()
})

watch(paginaActual, cargar)

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
</script>
