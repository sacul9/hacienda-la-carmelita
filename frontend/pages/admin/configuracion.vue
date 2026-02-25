<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-display font-bold text-tierra-900">Configuración</h1>
      <p class="text-gray-500 mt-1 text-sm">Valores de referencia actuales de la hacienda. Solo lectura en MVP.</p>
    </div>

    <!-- Sección: Información general -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <h2 class="text-base font-semibold text-gray-800 mb-4">Información general</h2>
      <dl class="divide-y divide-gray-50">
        <div
          v-for="item in infoGeneral"
          :key="item.label"
          class="flex items-center justify-between py-3"
        >
          <dt class="text-sm text-gray-500">{{ item.label }}</dt>
          <dd class="text-sm font-medium text-gray-800">{{ item.value }}</dd>
        </div>
      </dl>
    </div>

    <!-- Sección: Tarifas vigentes -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <h2 class="text-base font-semibold text-gray-800 mb-4">Tarifas vigentes</h2>
      <dl class="divide-y divide-gray-50">
        <div
          v-for="item in tarifas"
          :key="item.label"
          class="flex items-center justify-between py-3"
        >
          <dt class="text-sm text-gray-500">{{ item.label }}</dt>
          <dd class="text-sm font-medium text-gray-800">{{ item.value }}</dd>
        </div>
      </dl>
    </div>

    <!-- Sección: Políticas -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <h2 class="text-base font-semibold text-gray-800 mb-4">Políticas</h2>
      <dl class="divide-y divide-gray-50">
        <div
          v-for="item in politicas"
          :key="item.label"
          class="flex items-center justify-between py-3"
        >
          <dt class="text-sm text-gray-500">{{ item.label }}</dt>
          <dd class="text-sm font-medium text-gray-800">{{ item.value }}</dd>
        </div>
      </dl>
    </div>

    <!-- Sección: Integraciones activas -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <h2 class="text-base font-semibold text-gray-800 mb-4">Integraciones activas</h2>
      <div class="divide-y divide-gray-50">
        <div
          v-for="integracion in integraciones"
          :key="integracion.nombre"
          class="flex items-center justify-between py-3"
        >
          <span class="text-sm text-gray-700">{{ integracion.nombre }}</span>
          <span
            :class="integracion.badgeClass"
            class="px-2 py-0.5 rounded-full text-xs font-medium"
          >
            {{ integracion.estado }}
          </span>
        </div>
      </div>
    </div>

    <!-- Nota de producción -->
    <div class="bg-blue-50 border border-blue-200 rounded-2xl p-5 text-blue-800 text-sm">
      <p class="font-medium mb-1">Nota de producción</p>
      <p>Para modificar estos valores, actualiza las variables de entorno (<code class="bg-blue-100 px-1 py-0.5 rounded text-xs font-mono">.env</code>) en el servidor de producción (Railway/Render).</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Configuración — Admin Hacienda La Carmelita' })

const infoGeneral = [
  { label: 'Nombre', value: 'Hacienda La Carmelita' },
  { label: 'Ubicación', value: 'Lérida, Tolima, Colombia' },
  { label: 'Capacidad máxima', value: '18 huéspedes' },
  { label: 'Email', value: 'reservas@haciendalacarmelita.com' },
  { label: 'WhatsApp', value: '+573001234567' },
]

const tarifas = [
  { label: 'Temporada baja (L–J)', value: 'COP 800,000/noche' },
  { label: 'Temporada alta (V–D)', value: 'COP 1,200,000/noche' },
  { label: 'Estancia mínima', value: '2 noches' },
]

const politicas = [
  { label: 'Cancelación gratuita', value: 'Hasta 7 días antes del check-in' },
  { label: 'Check-in', value: '3:00 PM' },
  { label: 'Check-out', value: '12:00 PM' },
  { label: 'Mascotas', value: 'No permitidas' },
]

const integraciones = [
  { nombre: 'Wompi Sandbox', estado: 'Activo', badgeClass: 'bg-green-100 text-green-700' },
  { nombre: 'Stripe Sandbox', estado: 'Sandbox', badgeClass: 'bg-amber-100 text-amber-700' },
  { nombre: 'Claude API', estado: 'Conectado', badgeClass: 'bg-green-100 text-green-700' },
  { nombre: 'Twilio/WhatsApp', estado: 'Activo', badgeClass: 'bg-green-100 text-green-700' },
  { nombre: 'Lodgify (Channel Manager)', estado: 'Sandbox', badgeClass: 'bg-amber-100 text-amber-700' },
]
</script>
