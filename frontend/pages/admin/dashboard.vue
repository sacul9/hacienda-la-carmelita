<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-display font-bold text-tierra-900">Panel de Administración</h1>
      <p class="text-gray-500 mt-1 text-sm">
        Bienvenido, <span class="font-medium text-tierra-700">{{ authStore.usuario?.nombre }}</span>
      </p>
    </div>

    <!-- Loading skeleton -->
    <template v-if="loading">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="i in 4"
          :key="i"
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 animate-pulse"
        >
          <div class="h-8 w-8 bg-gray-200 rounded-lg mb-3" />
          <div class="h-8 w-20 bg-gray-200 rounded mb-2" />
          <div class="h-4 w-28 bg-gray-100 rounded" />
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 animate-pulse">
        <div class="h-5 w-40 bg-gray-200 rounded mb-4" />
        <div class="h-4 w-full bg-gray-100 rounded-full" />
      </div>
    </template>

    <!-- Error state -->
    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 rounded-2xl p-6 text-center"
    >
      <p class="text-red-700 font-medium">{{ error }}</p>
      <button
        class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors"
        @click="reload"
      >
        Reintentar
      </button>
    </div>

    <!-- Content -->
    <template v-else-if="data">
      <!-- KPI Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Reservas del mes -->
        <BaseCard :padding="false" class="p-5">
          <div class="flex flex-col gap-2">
            <div class="w-10 h-10 rounded-xl bg-tierra-50 flex items-center justify-center text-xl">
              📅
            </div>
            <p class="text-3xl font-bold text-tierra-800">{{ data.reservas_mes }}</p>
            <p class="text-sm text-gray-500">Reservas este mes</p>
          </div>
        </BaseCard>

        <!-- Ingresos del mes -->
        <BaseCard :padding="false" class="p-5">
          <div class="flex flex-col gap-2">
            <div class="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center text-xl">
              💰
            </div>
            <p class="text-2xl font-bold text-green-700 leading-tight">{{ formatCOP(data.ingresos_mes) }}</p>
            <p class="text-sm text-gray-500">Ingresos este mes</p>
          </div>
        </BaseCard>

        <!-- Pendientes -->
        <BaseCard :padding="false" class="p-5">
          <div class="flex flex-col gap-2">
            <div class="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center text-xl">
              ⏳
            </div>
            <p class="text-3xl font-bold text-amber-700">{{ data.reservas_pendientes }}</p>
            <p class="text-sm text-gray-500">Reservas pendientes</p>
          </div>
        </BaseCard>

        <!-- Próximas llegadas -->
        <BaseCard :padding="false" class="p-5">
          <div class="flex flex-col gap-2">
            <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-xl">
              🏠
            </div>
            <p class="text-3xl font-bold text-blue-700">{{ data.proximas_llegadas }}</p>
            <p class="text-sm text-gray-500">Llegadas en 7 días</p>
          </div>
        </BaseCard>
      </div>

      <!-- Barra de ocupación -->
      <BaseCard :padding="false" class="p-6">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-gray-800">Ocupación del mes</h2>
          <span class="text-sm font-bold text-tierra-700">{{ data.ocupacion_pct }}%</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-4 overflow-hidden">
          <div
            class="h-4 bg-tierra-700 rounded-full transition-all duration-500"
            :style="{ width: `${Math.min(data.ocupacion_pct, 100)}%` }"
          />
        </div>
        <div class="flex justify-between mt-1 text-xs text-gray-400">
          <span>0%</span>
          <span>100%</span>
        </div>
      </BaseCard>

      <!-- Últimas reservas -->
      <BaseCard :padding="false" class="p-6">
        <h2 class="text-base font-semibold text-gray-800 mb-4">Últimas reservas</h2>

        <div v-if="data.ultimas_reservas.length === 0" class="py-8 text-center text-gray-400 text-sm">
          No hay reservas recientes.
        </div>

        <div v-else class="overflow-x-auto -mx-6">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-100">
                <th class="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Código</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Huésped</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Check-in</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Estado</th>
                <th class="text-right px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Monto</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr
                v-for="r in data.ultimas_reservas"
                :key="r.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-6 py-3 font-mono text-xs text-tierra-700 font-semibold">{{ r.codigo }}</td>
                <td class="px-4 py-3 text-gray-800">{{ r.huesped_nombre }}</td>
                <td class="px-4 py-3 text-gray-600">{{ formatFecha(r.fecha_checkin) }}</td>
                <td class="px-4 py-3">
                  <span :class="estadoBadgeClass(r.estado)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                    {{ r.estado }}
                  </span>
                </td>
                <td class="px-6 py-3 text-right text-gray-800 font-medium">{{ formatCOP(r.precio_total_cop) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-4 pt-4 border-t border-gray-50">
          <NuxtLink
            to="/admin/reservas"
            class="text-sm text-tierra-700 hover:text-tierra-900 font-medium transition-colors"
          >
            Ver todas las reservas →
          </NuxtLink>
        </div>
      </BaseCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { DashboardData } from '~/composables/useAdmin'

definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Dashboard — Hacienda La Carmelita' })

const authStore = useAuthStore()
const { fetchDashboard } = useAdmin()

const loading = ref(true)
const error = ref<string | null>(null)
const data = ref<DashboardData | null>(null)

const cargar = async () => {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchDashboard()
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Error al cargar el dashboard'
  } finally {
    loading.value = false
  }
}

const reload = () => cargar()

onMounted(cargar)

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
