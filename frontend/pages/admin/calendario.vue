<template>
  <div class="space-y-6">
    <!-- Header con navegación de mes -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-display font-bold text-tierra-900">Calendario</h1>
        <p class="text-gray-500 mt-1 text-sm">Gestiona disponibilidad y bloqueos de fechas.</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors text-gray-600"
          @click="mesAnterior"
        >
          ←
        </button>
        <span class="text-sm font-semibold text-gray-700 min-w-[150px] text-center capitalize">
          {{ tituloMes }}
        </span>
        <button
          class="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors text-gray-600"
          @click="mesSiguiente"
        >
          →
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Calendario -->
      <div class="lg:col-span-2">
        <!-- Loading skeleton -->
        <div v-if="loading" class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 animate-pulse">
          <div class="grid grid-cols-7 gap-1 mb-2">
            <div v-for="i in 7" :key="i" class="h-6 bg-gray-100 rounded" />
          </div>
          <div class="grid grid-cols-7 gap-1">
            <div v-for="i in 35" :key="i" class="h-12 bg-gray-50 rounded" />
          </div>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
          <p class="text-red-700 font-medium">{{ error }}</p>
          <button class="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm" @click="cargar">
            Reintentar
          </button>
        </div>

        <!-- Grid calendario -->
        <div v-else class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <!-- Cabecera días semana -->
          <div class="grid grid-cols-7 border-b border-gray-100">
            <div
              v-for="dia in ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']"
              :key="dia"
              class="py-2 text-center text-xs font-semibold text-gray-400 uppercase"
            >
              {{ dia }}
            </div>
          </div>

          <!-- Celdas de días -->
          <div class="grid grid-cols-7">
            <!-- Días vacíos al inicio -->
            <div
              v-for="i in diasVaciosInicio"
              :key="`empty-${i}`"
              class="h-14 border-b border-r border-gray-50"
            />
            <!-- Días del mes -->
            <div
              v-for="dia in diasDelMes"
              :key="dia"
              :class="[
                'h-14 border-b border-r border-gray-50 p-1 relative',
                claseDia(dia),
              ]"
            >
              <span
                :class="[
                  'absolute top-1 left-1.5 text-xs font-medium',
                  esHoy(dia) ? 'text-tierra-700 font-bold' : 'text-gray-500',
                ]"
              >
                {{ dia }}
              </span>
              <!-- Indicador -->
              <div v-if="tieneReserva(dia)" class="absolute bottom-1 left-1 right-1">
                <div class="h-1.5 bg-tierra-500 rounded-full opacity-80" />
              </div>
              <div v-else-if="tieneBloqueo(dia)" class="absolute bottom-1 left-1 right-1">
                <div class="h-1.5 bg-red-400 rounded-full opacity-80" />
              </div>
            </div>
          </div>
        </div>

        <!-- Leyenda -->
        <div class="flex flex-wrap gap-4 mt-3 text-xs text-gray-500">
          <div class="flex items-center gap-1.5">
            <div class="w-3 h-3 rounded-full bg-tierra-500 opacity-80" />
            <span>Con reserva</span>
          </div>
          <div class="flex items-center gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red-400 opacity-80" />
            <span>Bloqueado</span>
          </div>
          <div class="flex items-center gap-1.5">
            <div class="w-3 h-3 rounded-full bg-gray-200" />
            <span>Disponible</span>
          </div>
        </div>
      </div>

      <!-- Panel lateral -->
      <div class="space-y-4">
        <!-- Crear bloqueo -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 class="text-sm font-semibold text-gray-800 mb-4">Crear bloqueo</h2>

          <div class="space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">Desde</label>
              <input
                v-model="nuevoBloqueo.fecha_inicio"
                type="date"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tierra-300"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">Hasta</label>
              <input
                v-model="nuevoBloqueo.fecha_fin"
                type="date"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tierra-300"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">Motivo (opcional)</label>
              <input
                v-model="nuevoBloqueo.motivo"
                type="text"
                placeholder="ej. Mantenimiento, uso personal..."
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tierra-300"
              />
            </div>

            <div v-if="errorBloqueo" class="text-xs text-red-600 bg-red-50 rounded-lg p-2">
              {{ errorBloqueo }}
            </div>

            <button
              :disabled="creandoBloqueo || !nuevoBloqueo.fecha_inicio || !nuevoBloqueo.fecha_fin"
              :class="[
                'w-full py-2 rounded-lg text-sm font-medium transition-colors',
                creandoBloqueo || !nuevoBloqueo.fecha_inicio || !nuevoBloqueo.fecha_fin
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-tierra-700 text-white hover:bg-tierra-800',
              ]"
              @click="crearBloqueo"
            >
              {{ creandoBloqueo ? 'Guardando…' : 'Bloquear fechas' }}
            </button>
          </div>
        </div>

        <!-- Lista de bloqueos activos -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 class="text-sm font-semibold text-gray-800 mb-3">Bloqueos activos</h2>

          <div v-if="!data || bloqueos.length === 0" class="text-xs text-gray-400 text-center py-4">
            No hay bloqueos en este mes.
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="b in bloqueos"
              :key="b.id"
              class="flex items-start justify-between gap-2 p-2 bg-red-50 rounded-lg"
            >
              <div>
                <p class="text-xs font-medium text-red-800">
                  {{ formatFecha(b.fecha_inicio) }} → {{ formatFecha(b.fecha_fin) }}
                </p>
                <p v-if="b.motivo" class="text-xs text-red-600 mt-0.5">{{ b.motivo }}</p>
              </div>
              <button
                class="text-red-500 hover:text-red-700 text-xs font-medium shrink-0"
                @click="eliminarBloqueo(b.id)"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Calendario — Hacienda La Carmelita' })

const config = useRuntimeConfig()
const authStore = useAuthStore()
const { fetchCalendario } = useAdmin()

// ─── Estado ──────────────────────────────────────────────────────────────────
const mesActual = ref(new Date().toISOString().slice(0, 7)) // "2025-02"
const data = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const nuevoBloqueo = ref({ fecha_inicio: '', fecha_fin: '', motivo: '' })
const creandoBloqueo = ref(false)
const errorBloqueo = ref<string | null>(null)

// ─── Computed ─────────────────────────────────────────────────────────────────
const tituloMes = computed(() => {
  const [y, m] = mesActual.value.split('-').map(Number)
  return new Date(y, m - 1, 1).toLocaleDateString('es-CO', { month: 'long', year: 'numeric' })
})

const diasDelMes = computed(() => {
  if (!data.value) return []
  return Array.from({ length: data.value.dias }, (_, i) => i + 1)
})

const diasVaciosInicio = computed(() => {
  const [y, m] = mesActual.value.split('-').map(Number)
  return new Date(y, m - 1, 1).getDay() // 0=Dom
})

const bloqueos = computed(() => {
  if (!data.value) return []
  return data.value.eventos.filter((e: any) => e.tipo === 'bloqueo')
})

const reservas = computed(() => {
  if (!data.value) return []
  return data.value.eventos.filter((e: any) => e.tipo === 'reserva')
})

// ─── Helpers ──────────────────────────────────────────────────────────────────
const diasReservados = computed(() => {
  const set = new Set<number>()
  const [y, m] = mesActual.value.split('-').map(Number)
  for (const r of reservas.value) {
    let d = new Date(r.fecha_inicio + 'T00:00:00')
    const fin = new Date(r.fecha_fin + 'T00:00:00')
    while (d < fin) {
      if (d.getFullYear() === y && d.getMonth() + 1 === m) set.add(d.getDate())
      d.setDate(d.getDate() + 1)
    }
  }
  return set
})

const diasBloqueados = computed(() => {
  const set = new Set<number>()
  const [y, m] = mesActual.value.split('-').map(Number)
  for (const b of bloqueos.value) {
    let d = new Date(b.fecha_inicio + 'T00:00:00')
    const fin = new Date(b.fecha_fin + 'T00:00:00')
    while (d <= fin) {
      if (d.getFullYear() === y && d.getMonth() + 1 === m) set.add(d.getDate())
      d.setDate(d.getDate() + 1)
    }
  }
  return set
})

const tieneReserva = (dia: number) => diasReservados.value.has(dia)
const tieneBloqueo = (dia: number) => diasBloqueados.value.has(dia)

const esHoy = (dia: number) => {
  const hoy = new Date()
  const [y, m] = mesActual.value.split('-').map(Number)
  return hoy.getFullYear() === y && hoy.getMonth() + 1 === m && hoy.getDate() === dia
}

const claseDia = (dia: number) => {
  if (esHoy(dia)) return 'bg-tierra-50 ring-2 ring-inset ring-tierra-400'
  if (tieneReserva(dia)) return 'bg-tierra-50'
  if (tieneBloqueo(dia)) return 'bg-red-50'
  return 'bg-white hover:bg-gray-50'
}

const formatFecha = (iso: string) => {
  const clean = iso.split('T')[0]
  const [y, m, d] = clean.split('-')
  const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
  return `${d} ${meses[parseInt(m) - 1]}. ${y}`
}

// ─── Acciones ─────────────────────────────────────────────────────────────────
const cargar = async () => {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchCalendario(mesActual.value)
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Error al cargar calendario'
  } finally {
    loading.value = false
  }
}

const mesAnterior = () => {
  const [y, m] = mesActual.value.split('-').map(Number)
  const d = new Date(y, m - 2, 1)
  mesActual.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

const mesSiguiente = () => {
  const [y, m] = mesActual.value.split('-').map(Number)
  const d = new Date(y, m, 1)
  mesActual.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

const crearBloqueo = async () => {
  errorBloqueo.value = null
  creandoBloqueo.value = true
  try {
    await $fetch(`${config.public.apiBase}/admin/bloqueos`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${authStore.token}` },
      body: {
        fecha_inicio: nuevoBloqueo.value.fecha_inicio,
        fecha_fin: nuevoBloqueo.value.fecha_fin,
        motivo: nuevoBloqueo.value.motivo || null,
      },
    })
    nuevoBloqueo.value = { fecha_inicio: '', fecha_fin: '', motivo: '' }
    await cargar()
  } catch (e: any) {
    errorBloqueo.value = e?.data?.detail ?? 'Error al crear bloqueo'
  } finally {
    creandoBloqueo.value = false
  }
}

const eliminarBloqueo = async (id: string) => {
  try {
    await $fetch(`${config.public.apiBase}/admin/bloqueos/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    await cargar()
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Error al eliminar bloqueo'
  }
}

onMounted(cargar)
watch(mesActual, cargar)
</script>
