<template>
  <div class="min-h-screen flex bg-gray-50">
    <!-- Sidebar admin -->
    <AdminSidebar />
    <!-- Contenido principal -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <AdminHeader />
      <main class="flex-1 overflow-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// SEC-003: Auth guard — solo staff/admin puede acceder al panel
const authStore = useAuthStore()
const { refreshToken } = useAuth()

onMounted(async () => {
  // Si no hay sesión en memoria, intentar refrescar desde la cookie httpOnly
  if (!authStore.isAuthenticated) {
    const token = await refreshToken()
    if (!token) {
      await navigateTo('/auth/login')
      return
    }
  }
  // Verificar rol suficiente (staff o admin)
  if (!authStore.isStaff) {
    await navigateTo('/')
  }
})
</script>
