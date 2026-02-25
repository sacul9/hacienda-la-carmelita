<template>
  <aside class="w-64 bg-tierra-900 text-white flex flex-col min-h-screen">
    <div class="p-6 border-b border-tierra-800">
      <h2 class="font-display font-semibold text-lg">La Carmelita</h2>
      <p class="text-tierra-300 text-xs mt-0.5">Panel de Administración</p>
    </div>
    <nav class="flex-1 p-4 space-y-1">
      <NuxtLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-tierra-200 hover:bg-tierra-800 hover:text-white transition-colors"
        active-class="bg-tierra-800 text-white"
      >
        <span>{{ item.icon }}</span>
        {{ item.label }}
      </NuxtLink>
    </nav>
    <div class="p-4 border-t border-tierra-800">
      <button class="w-full text-left text-sm text-tierra-300 hover:text-white transition-colors">
        Cerrar sesión
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
const navItems = [
  { path: '/admin/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/admin/reservas', label: 'Reservas', icon: '📋' },
  { path: '/admin/calendario', label: 'Calendario', icon: '📅' },
  { path: '/admin/precios', label: 'Precios', icon: '💰' },
  { path: '/admin/huespedes', label: 'Huéspedes', icon: '👥' },
  { path: '/admin/reportes', label: 'Reportes', icon: '📈' },
  { path: '/admin/sync', label: 'Sincronización', icon: '🔄' },
  { path: '/admin/agentes', label: 'Agentes IA', icon: '🤖' },
  { path: '/admin/configuracion', label: 'Configuración', icon: '⚙️' },
]
</script>
