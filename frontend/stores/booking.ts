import { defineStore } from 'pinia'

interface SKU {
  id: string
  nombre: string
  precio_cop: number
  precio_usd: number
}

interface AddOn {
  id: string
  nombre: string
  precio_cop: number
  cantidad: number
}

interface HuespedData {
  nombre: string
  apellido: string
  email: string
  telefono: string
  pais: string
  huespedes: number
  notas: string
}

interface BookingState {
  fechaCheckin: string | null
  fechaCheckout: string | null
  noches: number
  skuSeleccionado: SKU | null
  addOns: AddOn[]
  huesped: HuespedData | null
  otpVerificado: boolean
  otpId: string | null
  otpToken: string | null
  reservaId: string | null
  codigoReserva: string | null
  precioTotal: number
  moneda: 'COP' | 'USD'
}

export const useBookingStore = defineStore('booking', {
  state: (): BookingState => ({
    fechaCheckin: null,
    fechaCheckout: null,
    noches: 0,
    skuSeleccionado: null,
    addOns: [],
    huesped: null,
    otpVerificado: false,
    otpId: null,
    otpToken: null,
    reservaId: null,
    codigoReserva: null,
    precioTotal: 0,
    moneda: 'COP',
  }),

  getters: {
    puedeAvanzarPaso1: (state) =>
      Boolean(state.fechaCheckin && state.fechaCheckout && state.noches >= 2),

    puedeAvanzarPaso2: (state) =>
      Boolean(state.skuSeleccionado),

    puedeAvanzarPaso3: (state) =>
      Boolean(state.huesped?.email && state.huesped?.telefono),

    puedeAvanzarPaso4: (state) =>
      state.otpVerificado,

    resumenPrecio: (state) => {
      const base = state.skuSeleccionado?.precio_cop ?? 0
      const addOnsTotal = state.addOns.reduce((sum, a) => sum + a.precio_cop * a.cantidad, 0)
      return {
        base: base * state.noches,
        addOns: addOnsTotal,
        total: (base * state.noches) + addOnsTotal,
      }
    },
  },

  actions: {
    setFechas(checkin: string, checkout: string) {
      this.fechaCheckin = checkin
      this.fechaCheckout = checkout
      const d1 = new Date(checkin)
      const d2 = new Date(checkout)
      this.noches = Math.round((d2.getTime() - d1.getTime()) / (1000 * 60 * 60 * 24))
    },

    setSKU(sku: SKU) {
      this.skuSeleccionado = sku
    },

    toggleAddOn(addon: AddOn) {
      const idx = this.addOns.findIndex(a => a.id === addon.id)
      if (idx === -1) {
        this.addOns.push(addon)
      } else {
        this.addOns.splice(idx, 1)
      }
    },

    setHuesped(data: HuespedData) {
      this.huesped = data
    },

    confirmarOTP(token: string) {
      this.otpVerificado = true
      this.otpToken = token
    },

    setReserva(id: string, codigo: string) {
      this.reservaId = id
      this.codigoReserva = codigo
    },

    resetBooking() {
      this.$reset()
    },
  },

  // Estado de reserva en sesión — no persistir entre recargas (flujo OTP)
})
