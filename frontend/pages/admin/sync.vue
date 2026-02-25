<template>
  <div class="min-h-screen bg-crema-50">
    <div class="container-site px-4 py-8 max-w-5xl mx-auto">

      <!-- Header -->
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="font-display text-2xl font-bold text-tierra-800">Channel Manager</h1>
          <p class="text-gray-500 text-sm mt-1">Sincronización con Airbnb y Booking.com vía Lodgify</p>
        </div>
        <button
          @click="forzarSync"
          :disabled="sincronizando"
          class="px-5 py-2.5 rounded-xl bg-tierra-800 hover:bg-tierra-900 disabled:opacity-50 text-white font-semibold text-sm transition-colors flex items-center gap-2"
        >
          <span v-if="sincronizando" class="animate-spin">⟳</span>
          <span v-else>⟳</span>
          {{ sincronizando ? 'Sincronizando...' : 'Sincronizar ahora' }}
        </button>
      </div>

      <!-- Loading / Error -->
      <div v-if="loading" class="text-center py-16 text-gray-400">Cargando estado...</div>
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm mb-6">
        Error al cargar el estado: {{ error }}
        <button @click="cargar" class="ml-2 underline">Reintentar</button>
      </div>

      <template v-else-if="syncEstado">

        <!-- KPI Cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <!-- Estado general -->
          <div class="bg-white rounded-xl border p-4 col-span-2 md:col-span-1"
               :class="estadoBorderClass">
            <p class="text-xs text-gray-500 mb-1">Estado actual</p>
            <div class="flex items-center gap-2">
              <span class="text-2xl">{{ estadoEmoji }}</span>
              <span class="font-bold text-lg capitalize" :class="estadoTextClass">
                {{ estadoLabel }}
              </span>
            </div>
          </div>

          <!-- Última sincronización -->
          <div class="bg-white rounded-xl border border-tierra-100 p-4">
            <p class="text-xs text-gray-500 mb-1">Última sync</p>
            <p class="font-bold text-tierra-800">
              {{ syncEstado.minutos_desde_ultima_sync != null
                  ? `hace ${syncEstado.minutos_desde_ultima_sync} min`
                  : 'Nunca' }}
            </p>
          </div>

          <!-- Importadas hoy -->
          <div class="bg-white rounded-xl border border-tierra-100 p-4">
            <p class="text-xs text-gray-500 mb-1">Importadas hoy</p>
            <p class="font-display text-2xl font-bold text-tierra-800">
              {{ syncEstado.total_importadas_hoy }}
            </p>
          </div>

          <!-- Conflictos -->
          <div class="bg-white rounded-xl border p-4"
               :class="syncEstado.conflictos_pendientes > 0 ? 'border-red-200 bg-red-50' : 'border-tierra-100'">
            <p class="text-xs text-gray-500 mb-1">Conflictos hoy</p>
            <p class="font-display text-2xl font-bold"
               :class="syncEstado.conflictos_pendientes > 0 ? 'text-red-700' : 'text-tierra-800'">
              {{ syncEstado.conflictos_pendientes }}
            </p>
          </div>
        </div>

        <!-- Alerta si >30 min sin sync -->
        <div
          v-if="syncEstado.estado_actual === 'alerta'"
          class="mb-6 bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3"
        >
          <span class="text-amber-500 text-xl">⚠️</span>
          <div>
            <p class="font-semibold text-amber-800">Sin sincronización hace {{ syncEstado.minutos_desde_ultima_sync }} minutos</p>
            <p class="text-sm text-amber-700 mt-0.5">El worker de Celery puede estar detenido. Verifica que el servicio esté corriendo.</p>
          </div>
        </div>

        <!-- Tabla de logs -->
        <div class="bg-white rounded-2xl border border-tierra-100 overflow-hidden">
          <div class="px-6 py-4 border-b border-tierra-100">
            <h2 class="font-semibold text-tierra-800">Historial de sincronizaciones (últimas 20)</h2>
          </div>

          <div v-if="syncEstado.logs.length === 0" class="px-6 py-12 text-center text-gray-400">
            <p class="text-4xl mb-2">📡</p>
            <p>Sin sincronizaciones registradas</p>
            <p class="text-sm mt-1">Haz clic en "Sincronizar ahora" para la primera sync</p>
          </div>

          <table v-else class="w-full text-sm">
            <thead>
              <tr class="border-b border-tierra-50 bg-crema-50">
                <th class="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Fecha</th>
                <th class="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Canal</th>
                <th class="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Estado</th>
                <th class="text-right px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Import.</th>
                <th class="text-right px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Duración</th>
                <th class="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Por</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="log in syncEstado.logs"
                :key="log.id"
                class="border-b border-tierra-50 hover:bg-crema-50 transition-colors"
              >
                <td class="px-6 py-3 text-gray-600 font-mono text-xs">{{ formatFecha(log.created_at) }}</td>
                <td class="px-6 py-3">
                  <span class="px-2 py-1 rounded-full text-xs font-semibold bg-tierra-50 text-tierra-700 capitalize">
                    {{ log.canal }}
                  </span>
                </td>
                <td class="px-6 py-3">
                  <span
                    class="px-2 py-1 rounded-full text-xs font-semibold"
                    :class="{
                      'bg-green-100 text-green-700': log.estado === 'ok',
                      'bg-red-100 text-red-700': log.estado === 'error',
                      'bg-amber-100 text-amber-700': log.estado === 'en_progreso',
                    }"
                  >
                    {{ log.estado === 'ok' ? '✓ OK' : log.estado === 'error' ? '✗ Error' : '⟳ En progreso' }}
                  </span>
                  <p v-if="log.mensaje_error" class="text-red-500 text-xs mt-1">{{ log.mensaje_error }}</p>
                </td>
                <td class="px-6 py-3 text-right">
                  <span v-if="log.reservas_importadas > 0" class="text-tierra-700 font-semibold">+{{ log.reservas_importadas }}</span>
                  <span v-else class="text-gray-400">—</span>
                  <span v-if="log.conflictos_detectados > 0" class="ml-1 text-red-500 text-xs">⚠{{ log.conflictos_detectados }}</span>
                </td>
                <td class="px-6 py-3 text-right text-gray-500">
                  {{ log.duracion_ms ? `${log.duracion_ms}ms` : '—' }}
                </td>
                <td class="px-6 py-3 text-gray-500 text-xs truncate max-w-[120px]">{{ log.iniciado_por }}</td>
              </tr>
            </tbody>
          </table>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin' })

useSeoMeta({
  title: 'Channel Manager — Admin Hacienda La Carmelita',
})

const { fetchSync, forzarSync: forzarSyncApi } = useAdmin()

const loading = ref(true)
const error = ref<string | null>(null)
const sincronizando = ref(false)
const syncEstado = ref<any>(null)

async function cargar() {
  loading.value = true
  error.value = null
  try {
    syncEstado.value = await fetchSync()
  } catch (e: any) {
    error.value = e?.message || 'Error desconocido'
  } finally {
    loading.value = false
  }
}

async function forzarSync() {
  sincronizando.value = true
  try {
    await forzarSyncApi()
    await new Promise(r => setTimeout(r, 1500))
    await cargar()
  } catch (e: any) {
    error.value = e?.message || 'Error al forzar sync'
  } finally {
    sincronizando.value = false
  }
}

const estadoEmoji = computed(() => {
  const e = syncEstado.value?.estado_actual
  if (e === 'ok') return '✅'
  if (e === 'error') return '❌'
  if (e === 'alerta') return '⚠️'
  return '📡'
})

const estadoLabel = computed(() => {
  const e = syncEstado.value?.estado_actual
  if (e === 'ok') return 'OK'
  if (e === 'error') return 'Error'
  if (e === 'alerta') return 'Alerta'
  return 'Sin datos'
})

const estadoBorderClass = computed(() => {
  const e = syncEstado.value?.estado_actual
  if (e === 'ok') return 'border-green-200 bg-green-50'
  if (e === 'error') return 'border-red-200 bg-red-50'
  if (e === 'alerta') return 'border-amber-200 bg-amber-50'
  return 'border-tierra-100'
})

const estadoTextClass = computed(() => {
  const e = syncEstado.value?.estado_actual
  if (e === 'ok') return 'text-green-700'
  if (e === 'error') return 'text-red-700'
  if (e === 'alerta') return 'text-amber-700'
  return 'text-gray-500'
})

function formatFecha(iso: string) {
  const d = new Date(iso)
  return d.toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' })
}

onMounted(cargar)
</script>
