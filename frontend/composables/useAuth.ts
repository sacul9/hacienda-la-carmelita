/**
 * Composable de autenticación — Sprint 1
 * Gestiona registro, login, logout y refresh de tokens.
 */
export const useAuth = () => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  const router = useRouter()

  const loading = ref(false)
  const error = ref<string | null>(null)

  const registro = async (data: {
    email: string
    nombre: string
    apellido: string
    telefono: string
    pais?: string
    idioma?: string
  }) => {
    loading.value = true
    error.value = null
    try {
      return await $fetch<{
        id: string; email: string; nombre: string; apellido: string
        rol: string; email_verificado: boolean; telefono_verificado: boolean
      }>(`${config.public.apiBase}/auth/registro`, { method: 'POST', body: data })
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Error al registrar usuario'
      throw e
    } finally {
      loading.value = false
    }
  }

  const login = async (email: string, password: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await $fetch<{
        access_token: string; token_type: string; usuario_id: string; rol: string
      }>(`${config.public.apiBase}/auth/login`, {
        method: 'POST',
        body: { email, password },
        credentials: 'include',
      })
      const perfil = await $fetch<{
        id: string; email: string; nombre: string; apellido: string; rol: string
        email_verificado: boolean; telefono_verificado: boolean
      }>(`${config.public.apiBase}/auth/me`, {
        headers: { Authorization: `Bearer ${response.access_token}` },
      })
      authStore.setAuth(
        { id: perfil.id, email: perfil.email, nombre: perfil.nombre, apellido: perfil.apellido, rol: perfil.rol as any },
        response.access_token,
      )
      await router.push('/admin/dashboard')
      return response
    } catch (e: any) {
      error.value = e?.data?.detail ?? 'Credenciales inválidas'
      throw e
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await $fetch(`${config.public.apiBase}/auth/logout`, { method: 'DELETE', credentials: 'include' })
    } catch { /* ignorar */ } finally {
      authStore.logout()
      await router.push('/')
    }
  }

  const refreshToken = async () => {
    try {
      const response = await $fetch<{ access_token: string; usuario_id: string; rol: string }>(
        `${config.public.apiBase}/auth/refresh`, { method: 'POST', credentials: 'include' }
      )
      if (authStore.usuario) authStore.setAuth(authStore.usuario, response.access_token)
      return response.access_token
    } catch {
      authStore.logout()
      return null
    }
  }

  return { loading: readonly(loading), error: readonly(error), registro, login, logout, refreshToken }
}
