<template>
  <div>

    <!-- Resumen de fechas seleccionadas -->
    <div class="grid grid-cols-2 gap-3 mb-5">
      <button
        type="button"
        :class="[
          'text-left p-3 rounded-xl border-2 transition',
          step === 'checkin'
            ? 'border-tierra-600 bg-tierra-50'
            : localCheckin ? 'border-gray-200 bg-white' : 'border-dashed border-gray-300 bg-gray-50'
        ]"
        @click="resetToCheckin"
      >
        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide mb-0.5">Check-in</p>
        <p :class="localCheckin ? 'text-tierra-800 font-semibold text-sm' : 'text-gray-400 text-sm'">
          {{ localCheckin ? formatDisplay(localCheckin) : 'Elige fecha' }}
        </p>
      </button>
      <div
        :class="[
          'text-left p-3 rounded-xl border-2 transition',
          step === 'checkout'
            ? 'border-tierra-600 bg-tierra-50'
            : localCheckout ? 'border-gray-200 bg-white' : 'border-dashed border-gray-300 bg-gray-50'
        ]"
      >
        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide mb-0.5">Check-out</p>
        <p :class="localCheckout ? 'text-tierra-800 font-semibold text-sm' : 'text-gray-400 text-sm'">
          {{ localCheckout ? formatDisplay(localCheckout) : 'Elige fecha' }}
        </p>
      </div>
    </div>

    <!-- Instrucción -->
    <p class="text-sm text-center text-tierra-700 font-medium mb-4">
      {{ step === 'checkin' ? '👆 Selecciona tu fecha de llegada' : '👆 Selecciona tu fecha de salida' }}
    </p>

    <!-- Navegación de meses -->
    <div class="flex items-center justify-between mb-4 px-1">
      <button
        type="button"
        :disabled="!canGoPrev"
        class="p-2 rounded-lg hover:bg-gray-100 transition disabled:opacity-30 disabled:cursor-not-allowed text-lg"
        @click="prevMonth"
      >
        ‹
      </button>
      <div class="flex gap-4 sm:gap-10">
        <span
          v-for="m in months"
          :key="`${m.year}-${m.month}`"
          class="text-sm font-semibold text-tierra-800 w-32 sm:w-40 text-center"
        >
          {{ MONTH_NAMES[m.month] }} {{ m.year }}
        </span>
      </div>
      <button
        type="button"
        class="p-2 rounded-lg hover:bg-gray-100 transition text-lg"
        @click="nextMonth"
      >
        ›
      </button>
    </div>

    <!-- Calendarios -->
    <ClientOnly>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div v-for="cal in months" :key="`cal-${cal.year}-${cal.month}`">
          <!-- Cabecera días de la semana -->
          <div class="grid grid-cols-7 mb-1 select-none">
            <span
              v-for="dn in DAY_NAMES"
              :key="dn"
              class="text-center text-xs text-gray-400 font-medium py-1"
            >{{ dn }}</span>
          </div>

          <!-- Días del mes -->
          <div class="grid grid-cols-7">
            <!-- Espacios para alinear el primer día -->
            <div v-for="n in cal.offset" :key="`empty-${n}`" />

            <!-- Cada día — usa <button> para garantizar interactividad nativa en todos los navegadores -->
            <button
              v-for="dayObj in cal.dayObjects"
              :key="dayObj.day"
              type="button"
              :disabled="dayObj.isPast"
              :class="dayClasses(dayObj)"
              @click="selectDay(cal.year, cal.month, dayObj.day)"
              @mouseenter="onHover(cal.year, cal.month, dayObj.day)"
              @mouseleave="hoverDay = null"
            >
              {{ dayObj.day }}
            </button>
          </div>
        </div>
      </div>

      <!-- Fallback SSR: calendario estático sin interactividad -->
      <template #fallback>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div v-for="cal in months" :key="`ssr-${cal.year}-${cal.month}`">
            <div class="grid grid-cols-7 mb-1 select-none">
              <span
                v-for="dn in DAY_NAMES"
                :key="dn"
                class="text-center text-xs text-gray-400 font-medium py-1"
              >{{ dn }}</span>
            </div>
            <div class="grid grid-cols-7">
              <div v-for="n in cal.offset" :key="`fempty-${n}`" />
              <div
                v-for="d in cal.days"
                :key="d"
                class="h-9 w-full flex items-center justify-center text-sm rounded"
              >{{ d }}</div>
            </div>
          </div>
        </div>
      </template>
    </ClientOnly>

    <!-- Badge de noches -->
    <div v-if="nights > 0" class="mt-5 flex justify-center">
      <span
        :class="[
          'inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-semibold',
          nights >= 2
            ? 'bg-tierra-50 text-tierra-800 border border-tierra-200'
            : 'bg-red-50 text-red-700 border border-red-200'
        ]"
      >
        {{ nights }} {{ nights === 1 ? 'noche' : 'noches' }}
        <span v-if="nights < 2" class="font-normal text-xs">· mínimo 2</span>
      </span>
    </div>

  </div>
</template>

<script setup lang="ts">
// ── Props / emits ──────────────────────────────────────────────────────────────
const props = defineProps<{ checkin: string; checkout: string }>()
const emit = defineEmits<{
  'update:checkin': [v: string]
  'update:checkout': [v: string]
}>()

// ── Constantes ─────────────────────────────────────────────────────────────────
const MONTH_NAMES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const DAY_NAMES   = ['Do','Lu','Ma','Mi','Ju','Vi','Sá']

// ── Estado local (reacciona inmediatamente sin esperar el ciclo del padre) ─────
const localCheckin  = ref(props.checkin  ?? '')
const localCheckout = ref(props.checkout ?? '')

// Sincronizar si el padre cambia los valores externamente
watch(() => props.checkin,  v => { localCheckin.value  = v ?? '' })
watch(() => props.checkout, v => { localCheckout.value = v ?? '' })

const step     = ref<'checkin' | 'checkout'>('checkin')
const hoverDay = ref<Date | null>(null)

// ── Fecha de hoy — calculada en el cliente para evitar hydration mismatch ─────
// Se usa useNuxtApp().ssrContext para detectar si estamos en SSR;
// en SSR se usa una sentinel que no producirá diferencias de timezone.
const todayISO = ref('')
onMounted(() => {
  const d = new Date()
  d.setHours(0, 0, 0, 0)
  todayISO.value = toISO(d.getFullYear(), d.getMonth(), d.getDate())
})

// ── Calendario ─────────────────────────────────────────────────────────────────
const viewYear  = ref(new Date().getFullYear())
const viewMonth = ref(new Date().getMonth())

interface DayObject {
  day: number
  isPast: boolean
  isToday: boolean
  iso: string
}

interface MonthData {
  year: number
  month: number
  days: number
  offset: number
  dayObjects: DayObject[]
}

const months = computed<MonthData[]>(() => {
  const out: MonthData[] = []
  for (let i = 0; i < 2; i++) {
    let mo = viewMonth.value + i
    let yr = viewYear.value
    if (mo > 11) { mo -= 12; yr++ }
    const totalDays = new Date(yr, mo + 1, 0).getDate()
    const offset    = new Date(yr, mo, 1).getDay()

    const dayObjects: DayObject[] = []
    for (let d = 1; d <= totalDays; d++) {
      const iso = toISO(yr, mo, d)
      dayObjects.push({
        day:     d,
        isPast:  todayISO.value !== '' && iso < todayISO.value,
        isToday: todayISO.value !== '' && iso === todayISO.value,
        iso,
      })
    }

    out.push({ year: yr, month: mo, days: totalDays, offset, dayObjects })
  }
  return out
})

const canGoPrev = computed(() => {
  if (!todayISO.value) return false
  const now = new Date()
  return new Date(viewYear.value, viewMonth.value, 1) >
         new Date(now.getFullYear(), now.getMonth(), 1)
})

// ── Noches ─────────────────────────────────────────────────────────────────────
const nights = computed(() => {
  if (!localCheckin.value || !localCheckout.value) return 0
  return Math.round(
    (new Date(localCheckout.value + 'T12:00:00').getTime() -
     new Date(localCheckin.value  + 'T12:00:00').getTime()) / 86400000
  )
})

// ── Helpers ────────────────────────────────────────────────────────────────────
function toISO(y: number, mo: number, d: number) {
  const mm = String(mo + 1).padStart(2, '0')
  const dd = String(d).padStart(2, '0')
  return `${y}-${mm}-${dd}`
}

function dateMs(iso: string) {
  return new Date(iso + 'T12:00:00').getTime()
}

function formatDisplay(iso: string) {
  if (!iso) return ''
  return new Date(iso + 'T12:00:00').toLocaleDateString('es-CO', {
    day: 'numeric', month: 'short', year: 'numeric',
  })
}

// ── Selección ──────────────────────────────────────────────────────────────────
function selectDay(y: number, mo: number, d: number) {
  const iso = toISO(y, mo, d)
  if (todayISO.value && iso < todayISO.value) return

  if (step.value === 'checkin') {
    localCheckin.value  = iso
    localCheckout.value = ''
    emit('update:checkin',  iso)
    emit('update:checkout', '')
    step.value = 'checkout'
  } else {
    if (!localCheckin.value || dateMs(iso) <= dateMs(localCheckin.value)) {
      localCheckin.value  = iso
      localCheckout.value = ''
      emit('update:checkin',  iso)
      emit('update:checkout', '')
      step.value = 'checkout'
    } else {
      localCheckout.value = iso
      emit('update:checkout', iso)
      step.value = 'checkin'
    }
  }
}

function resetToCheckin() {
  localCheckin.value  = ''
  localCheckout.value = ''
  emit('update:checkin',  '')
  emit('update:checkout', '')
  step.value = 'checkin'
}

function onHover(y: number, mo: number, d: number) {
  const iso = toISO(y, mo, d)
  if (todayISO.value && iso < todayISO.value) { hoverDay.value = null; return }
  hoverDay.value = new Date(iso + 'T12:00:00')
}

// ── Clases CSS — recibe el objeto dayObj pre-computado ─────────────────────────
function dayClasses(dayObj: DayObject) {
  const { iso, isPast, isToday } = dayObj
  const ms   = dateMs(iso)
  const ciMs = localCheckin.value  ? dateMs(localCheckin.value)  : null
  const coMs = localCheckout.value ? dateMs(localCheckout.value) : null
  const hovMs = (step.value === 'checkout' && hoverDay.value && ciMs && hoverDay.value.getTime() > ciMs)
               ? hoverDay.value.getTime() : null

  const isCI   = ciMs !== null && ms === ciMs
  const isCO   = coMs !== null && ms === coMs
  const endMs  = coMs ?? hovMs
  const inRange = ciMs !== null && endMs !== null && ms > ciMs && ms < endMs

  return [
    'h-9 w-full flex items-center justify-center text-sm transition-colors rounded',
    isPast ? 'text-gray-300 cursor-not-allowed' : 'cursor-pointer',
    !isPast && !isCI && !isCO ? 'hover:bg-tierra-100' : '',
    isToday && !isCI && !isCO ? 'font-bold ring-1 ring-inset ring-tierra-300' : '',
    isCI  ? 'bg-tierra-800 text-white !rounded-l-full font-semibold' : '',
    isCO  ? 'bg-tierra-800 text-white !rounded-r-full font-semibold' : '',
    isCI && isCO ? '!rounded-full' : '',
    inRange && !isCI && !isCO ? 'bg-tierra-100 text-tierra-900 !rounded-none' : '',
  ]
}
</script>
