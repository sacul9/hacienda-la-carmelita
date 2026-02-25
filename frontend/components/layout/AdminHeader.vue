<template>
  <header class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
    <h1 class="text-lg font-semibold text-gray-900">{{ pageTitle }}</h1>
    <div class="flex items-center gap-3">
      <span class="text-sm text-gray-500">Admin</span>
    </div>
  </header>
</template>

<script setup lang="ts">
const route = useRoute()
const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/admin/dashboard': 'Dashboard',
    '/admin/reservas': 'Gestión de Reservas',
    '/admin/calendario': 'Calendario',
    '/admin/precios': 'Precios y Temporadas',
    '/admin/huespedes': 'Huéspedes',
    '/admin/reportes': 'Reportes',
    '/admin/configuracion': 'Configuración',
  }
  return titles[route.path] ?? 'Administración'
})
</script>
