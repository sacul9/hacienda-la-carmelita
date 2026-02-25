<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-display font-bold text-tierra-900">Precios</h1>
      <p class="text-gray-500 mt-1 text-sm">Gestiona las tarifas por temporada.</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 animate-pulse">
      <div class="h-4 w-32 bg-gray-200 rounded mb-4" />
      <div class="space-y-3">
        <div class="h-12 bg-gray-100 rounded-xl" />
        <div class="h-12 bg-gray-100 rounded-xl" />
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
      <p class="text-red-700 font-medium">{{ error }}</p>
      <button class="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm" @click="cargar">Reintentar</button>
    </div>

    <!-- Tarifas -->
    <div v-else class="space-y-4">
      <!-- Info -->
      <div class="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-sm text-amber-800">
        <strong>¿Cómo funcionan las tarifas?</strong> La tarifa <em>baja</em> aplica de lunes a jueves. La tarifa <em>alta</em> aplica viernes, sábado y domingo.
      </div>

      <!-- Cards de tarifas -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="tarifa in tarifas"
          :key="tarifa.temporada"
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6"
        >
          <div class="flex items-center justify-between mb-4">
            <div>
              <h3 class="text-base font-semibold text-gray-800 capitalize">
                Temporada {{ tarifa.temporada }}
              </h3>
              <p class="text-xs text-gray-400 mt-0.5">{{ tarifa.descripcion }}</p>
            </div>
            <span
              :class="tarifa.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
              class="text-xs font-medium px-2 py-0.5 rounded-full"
            >
              {{ tarifa.activo ? 'Activa' : 'Inactiva' }}
            </span>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Tarifa por noche (COP)</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">$</span>
              <input
                v-model.number="tarifa.tarifa_cop"
                type="number"
                min="1"
                step="50000"
                class="w-full border border-gray-200 rounded-xl pl-7 pr-4 py-2.5 text-sm font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-tierra-300"
              />
            </div>
            <p class="text-xs text-gray-400 mt-1">
              {{ formatCOP(tarifa.tarifa_cop) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Exito -->
      <div v-if="exito" class="bg-green-50 border border-green-200 rounded-xl p-3 text-sm text-green-700 text-center">
        Tarifas actualizadas correctamente
      </div>

      <!-- Error guardar -->
      <div v-if="errorGuardar" class="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700 text-center">
        {{ errorGuardar }}
      </div>

      <!-- Boton guardar -->
      <div class="flex justify-end">
        <button
          :disabled="guardando"
          :class="[
            'px-6 py-2.5 rounded-xl text-sm font-medium transition-colors',
            guardando ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-tierra-700 text-white hover:bg-tierra-800',
          ]"
          @click="guardar"
        >
          {{ guardando ? 'Guardando...' : 'Guardar cambios' }}
        </button>
      </div>

      <!-- Nota -->
      <p class="text-xs text-gray-400 text-center">
        Los cambios de precio aplican a nuevas reservas. Las reservas existentes no se ven afectadas.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Precios — Hacienda La Carmelita' })

const config = useRuntimeConfig()
const authStore = useAuthStore()

interface TarifaEditable {
  id: string | null
  temporada: string
  descripcion: string
  tarifa_cop: number
  activo: boolean
}

const loading = ref(true)
const error = ref<string | null>(null)
const tarifas = ref<TarifaEditable[]>([])
const guardando = ref(false)
const errorGuardar = ref<string | null>(null)
const exito = ref(false)

const headers = computed(() => ({
  Authorization: `Bearer ${authStore.token}`,
}))

const cargar = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await $fetch<{ tarifas: TarifaEditable[] }>(
      `${config.public.apiBase}/admin/precios`,
      { headers: headers.value }
    )
    tarifas.value = res.tarifas
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Error al cargar tarifas'
  } finally {
    loading.value = false
  }
}

const guardar = async () => {
  guardando.value = true
  errorGuardar.value = null
  exito.value = false
  try {
    await $fetch(`${config.public.apiBase}/admin/precios`, {
      method: 'PUT',
      headers: headers.value,
      body: { tarifas: tarifas.value },
    })
    exito.value = true
    setTimeout(() => { exito.value = false }, 3000)
  } catch (e: any) {
    errorGuardar.value = e?.data?.detail ?? 'Error al guardar tarifas'
  } finally {
    guardando.value = false
  }
}

const formatCOP = (v: number) =>
  `COP ${v.toLocaleString('es-CO', { minimumFractionDigits: 0 })}`

onMounted(cargar)
</script>
