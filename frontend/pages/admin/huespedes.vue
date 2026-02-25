<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <h1 class="text-2xl font-display font-bold text-tierra-900">Huéspedes</h1>
        <p class="text-gray-500 mt-1 text-sm">Huéspedes únicos derivados de las reservas.</p>
      </div>
      <span
        v-if="!loading && !error"
        class="px-3 py-1 rounded-full text-sm font-medium bg-tierra-100 text-tierra-800"
      >
        {{ huespedesFiltrados.length }} huésped{{ huespedesFiltrados.length !== 1 ? 'es' : '' }}
      </span>
    </div>

    <!-- Buscador -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
      <input
        v-model="busqueda"
        type="text"
        placeholder="Buscar por nombre o email..."
        class="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-tierra-300 focus:border-tierra-400 transition"
      />
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
            <div class="h-4 w-36 bg-gray-200 rounded" />
            <div class="h-4 w-48 bg-gray-100 rounded" />
            <div class="h-4 w-16 bg-gray-100 rounded" />
            <div class="h-4 w-28 bg-gray-100 rounded" />
            <div class="h-4 w-32 bg-gray-100 rounded" />
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

    <!-- Empty state (sin reservas en total) -->
    <div
      v-else-if="huespedes.length === 0"
      class="bg-white rounded-2xl border border-gray-100 shadow-sm p-12 text-center"
    >
      <p class="text-4xl mb-3">👥</p>
      <p class="text-gray-500 text-sm">Aún no hay huéspedes registrados.</p>
    </div>

    <!-- Empty state (sin resultados de búsqueda) -->
    <div
      v-else-if="huespedesFiltrados.length === 0"
      class="bg-white rounded-2xl border border-gray-100 shadow-sm p-10 text-center"
    >
      <p class="text-gray-400 text-sm">No se encontraron huéspedes que coincidan con "<span class="font-medium text-gray-600">{{ busqueda }}</span>".</p>
    </div>

    <!-- Tabla de huéspedes -->
    <template v-else>
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-100 bg-gray-50">
                <th class="text-left px-5 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide whitespace-nowrap">Nombre</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide whitespace-nowrap">Email</th>
                <th class="text-center px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide whitespace-nowrap">N.º reservas</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide whitespace-nowrap">Última visita</th>
                <th class="text-right px-5 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide whitespace-nowrap">Total gastado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr
                v-for="h in huespedesFiltrados"
                :key="h.email"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-5 py-3 text-gray-800 font-medium whitespace-nowrap">{{ h.nombre }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ h.email }}</td>
                <td class="px-4 py-3 text-center">
                  <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-tierra-100 text-tierra-800">
                    {{ h.numReservas }}
                  </span>
                </td>
                <td class="px-4 py-3 text-gray-600 text-xs whitespace-nowrap">{{ formatFecha(h.ultimaVisita) }}</td>
                <td class="px-5 py-3 text-right text-gray-800 font-medium whitespace-nowrap">{{ formatCOP(h.totalGastado) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="text-center text-xs text-gray-400">
        {{ huespedes.length }} huésped{{ huespedes.length !== 1 ? 'es' : '' }} únicos en total
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { ReservaAdminItem } from '~/composables/useAdmin'

definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Huéspedes — Admin Hacienda La Carmelita' })

interface HuespedAgrupado {
  nombre: string
  email: string
  numReservas: number
  ultimaVisita: string
  totalGastado: number
}

const { fetchReservas } = useAdmin()

const loading = ref(true)
const error = ref<string | null>(null)
const reservas = ref<ReservaAdminItem[]>([])
const busqueda = ref('')

const cargar = async () => {
  loading.value = true
  error.value = null
  try {
    // Cargar todas las páginas disponibles (máximo 500 registros en una sola llamada)
    const data = await fetchReservas({ page: 1, limit: 500 })
    reservas.value = data.items
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Error al cargar las reservas'
  } finally {
    loading.value = false
  }
}

// Derivar huéspedes únicos agrupando por huesped_email
const huespedes = computed<HuespedAgrupado[]>(() => {
  const mapa = new Map<string, HuespedAgrupado>()

  for (const r of reservas.value) {
    const email = r.huesped_email?.toLowerCase() ?? ''
    if (!email) continue

    if (mapa.has(email)) {
      const existente = mapa.get(email)!
      existente.numReservas += 1
      existente.totalGastado += r.precio_total_cop ?? 0
      // Conservar la fecha de check-in más reciente como "última visita"
      if (r.fecha_checkin > existente.ultimaVisita) {
        existente.ultimaVisita = r.fecha_checkin
        existente.nombre = r.huesped_nombre ?? existente.nombre
      }
    } else {
      mapa.set(email, {
        nombre: r.huesped_nombre ?? '',
        email,
        numReservas: 1,
        ultimaVisita: r.fecha_checkin,
        totalGastado: r.precio_total_cop ?? 0,
      })
    }
  }

  // Ordenar por total gastado descendente
  return Array.from(mapa.values()).sort((a, b) => b.totalGastado - a.totalGastado)
})

// Filtro de búsqueda en cliente
const huespedesFiltrados = computed<HuespedAgrupado[]>(() => {
  const q = busqueda.value.trim().toLowerCase()
  if (!q) return huespedes.value
  return huespedes.value.filter(
    (h) =>
      h.nombre.toLowerCase().includes(q) ||
      h.email.toLowerCase().includes(q)
  )
})

onMounted(() => cargar())

const formatCOP = (v: number) =>
  `COP ${v.toLocaleString('es-CO', { minimumFractionDigits: 0 })}`

const formatFecha = (iso: string) => {
  if (!iso) return '—'
  const clean = iso.split('T')[0]
  const [y, m, d] = clean.split('-')
  const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
  return `${d} ${meses[parseInt(m) - 1]}. ${y}`
}
</script>
