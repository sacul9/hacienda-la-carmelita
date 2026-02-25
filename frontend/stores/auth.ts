import { defineStore } from 'pinia'

interface Usuario {
  id: string
  email: string
  nombre: string
  apellido: string
  rol: 'guest' | 'staff' | 'admin'
}

interface AuthState {
  usuario: Usuario | null
  token: string | null
  isAuthenticated: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    usuario: null,
    token: null,
    isAuthenticated: false,
  }),

  getters: {
    isAdmin: (state) => state.usuario?.rol === 'admin',
    isStaff: (state) => ['admin', 'staff'].includes(state.usuario?.rol ?? ''),
  },

  actions: {
    setAuth(usuario: Usuario, token: string) {
      this.usuario = usuario
      this.token = token
      this.isAuthenticated = true
    },

    logout() {
      this.$reset()
    },
  },

  // SEC-002: sin persistencia en localStorage — el access token vive solo en memoria.
  // Al recargar la página, el layout admin llama refreshToken() que usa la httpOnly cookie.
})
