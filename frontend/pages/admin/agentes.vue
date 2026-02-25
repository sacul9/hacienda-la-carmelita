<template>
  <div class="min-h-screen bg-crema-50">
    <div class="container-site px-4 py-8 max-w-5xl mx-auto">

      <!-- Header -->
      <div class="mb-8 flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 class="font-display text-2xl font-bold text-tierra-800">Agentes de IA</h1>
          <p class="text-gray-500 text-sm mt-1">Generación automática de contenido SEO y GEO</p>
        </div>

        <!-- Botones de acción -->
        <div class="flex items-center gap-3 flex-wrap">
          <!-- Generar SEO -->
          <button
            @click="accionGenerarSEO"
            :disabled="seoGenerando"
            class="px-5 py-2.5 rounded-xl bg-tierra-800 hover:bg-tierra-900 disabled:opacity-50 text-white font-semibold text-sm transition-colors flex items-center gap-2"
          >
            <svg
              v-if="seoGenerando"
              class="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span v-else>✦</span>
            {{ seoGenerando ? 'Generando...' : 'Generar artículo SEO' }}
          </button>

          <!-- Generar GEO -->
          <button
            @click="accionGenerarGEO"
            :disabled="geoGenerando"
            class="px-5 py-2.5 rounded-xl border-2 border-tierra-800 text-tierra-800 hover:bg-tierra-50 disabled:opacity-50 font-semibold text-sm transition-colors flex items-center gap-2"
          >
            <svg
              v-if="geoGenerando"
              class="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span v-else>⊕</span>
            {{ geoGenerando ? 'Generando...' : 'Generar contenido GEO' }}
          </button>
        </div>
      </div>

      <!-- Mensajes de éxito -->
      <div
        v-if="mensajeSEO"
        class="mb-6 bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3"
      >
        <span class="text-green-600 text-lg">✓</span>
        <p class="text-green-800 text-sm font-medium">{{ mensajeSEO }}</p>
        <button @click="mensajeSEO = null" class="ml-auto text-green-500 hover:text-green-700 text-lg leading-none">×</button>
      </div>
      <div
        v-if="mensajeGEO"
        class="mb-6 bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3"
      >
        <span class="text-green-600 text-lg">✓</span>
        <p class="text-green-800 text-sm font-medium">{{ mensajeGEO }}</p>
        <button @click="mensajeGEO = null" class="ml-auto text-green-500 hover:text-green-700 text-lg leading-none">×</button>
      </div>

      <!-- Error general -->
      <div
        v-if="errorMsg"
        class="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm"
      >
        {{ errorMsg }}
        <button @click="errorMsg = null; cargar()" class="ml-2 underline">Reintentar</button>
      </div>

      <!-- KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">

        <!-- Total artículos publicados -->
        <div class="bg-white rounded-xl border border-tierra-100 p-5">
          <p class="text-xs text-gray-500 mb-2 uppercase tracking-wide font-medium">Artículos publicados</p>
          <div v-if="articuloCargando" class="animate-pulse bg-tierra-100 h-8 w-16 rounded" />
          <p v-else class="font-display text-3xl font-bold text-tierra-800">
            {{ articulosPublicados }}
          </p>
          <p class="text-xs text-gray-400 mt-1">de {{ articulos.length }} generados</p>
        </div>

        <!-- Último artículo -->
        <div class="bg-white rounded-xl border border-tierra-100 p-5">
          <p class="text-xs text-gray-500 mb-2 uppercase tracking-wide font-medium">Último artículo generado</p>
          <div v-if="articuloCargando" class="animate-pulse bg-tierra-100 h-8 w-40 rounded" />
          <p v-else class="font-bold text-tierra-800 text-base">
            {{ ultimaFecha }}
          </p>
          <p v-if="ultimoAutor && !articuloCargando" class="text-xs text-gray-400 mt-1">por {{ ultimoAutor }}</p>
        </div>

      </div>

      <!-- Tabla de artículos -->
      <div class="bg-white rounded-2xl border border-tierra-100 overflow-hidden mb-8">
        <div class="px-6 py-4 border-b border-tierra-100">
          <h2 class="font-semibold text-tierra-800">Artículos generados (últimos 10)</h2>
        </div>

        <!-- Skeleton carga -->
        <div v-if="articuloCargando" class="p-6 space-y-3">
          <div v-for="n in 3" :key="n" class="animate-pulse bg-tierra-50 h-10 rounded-lg" />
        </div>

        <!-- Sin artículos -->
        <div
          v-else-if="articulos.length === 0"
          class="px-6 py-12 text-center text-gray-500"
        >
          <p class="text-4xl mb-3">✦</p>
          <p class="font-medium">Sin artículos generados aún.</p>
          <p class="text-sm mt-1 text-gray-400">
            Usa el botón "Generar artículo SEO" para crear el primero.
          </p>
        </div>

        <!-- Tabla -->
        <table v-else class="w-full text-sm">
          <thead>
            <tr class="border-b border-tierra-50 bg-crema-50">
              <th class="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Título</th>
              <th class="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Estado</th>
              <th class="text-right px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Palabras clave</th>
              <th class="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Generado por</th>
              <th class="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="articulo in articulos.slice(0, 10)"
              :key="articulo.id"
              class="border-b border-tierra-50 hover:bg-crema-50 transition-colors cursor-pointer"
              @click="abrirArticulo(articulo.slug)"
            >
              <td class="px-6 py-3 text-tierra-800 font-medium max-w-xs">
                <span :title="articulo.titulo_es">
                  {{ truncar(articulo.titulo_es, 60) }}
                </span>
              </td>
              <td class="px-6 py-3">
                <span
                  class="px-2 py-1 rounded-full text-xs font-semibold"
                  :class="articulo.publicado
                    ? 'bg-green-100 text-green-700'
                    : 'bg-amber-100 text-amber-700'"
                >
                  {{ articulo.publicado ? 'Publicado' : 'Borrador' }}
                </span>
              </td>
              <td class="px-6 py-3 text-right text-gray-600">
                {{ articulo.palabras_clave?.length ?? 0 }}
              </td>
              <td class="px-6 py-3 text-gray-500 text-xs">
                {{ articulo.autor_agente ?? '—' }}
              </td>
              <td class="px-6 py-3 text-gray-500 text-xs font-mono">
                {{ formatFecha(articulo.created_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Sección GEO -->
      <div class="bg-white rounded-2xl border border-tierra-100 p-6">
        <h2 class="font-semibold text-tierra-800 mb-2">Estado del contenido GEO</h2>
        <p class="text-sm text-gray-600 leading-relaxed mb-4">
          El archivo <code class="bg-tierra-50 text-tierra-700 px-1.5 py-0.5 rounded text-xs font-mono">llms.txt</code>
          optimiza la visibilidad de la hacienda en buscadores con IA (ChatGPT, Perplexity, Gemini).
        </p>
        <a
          :href="`${apiBase}/agentes/geo/llms.txt`"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center text-dorado-600 hover:text-dorado-700 font-semibold text-sm transition-colors"
        >
          Ver llms.txt actual →
        </a>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin' })

useSeoMeta({
  title: 'Agentes de IA — Admin Hacienda La Carmelita',
})

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const { articulos, articuloCargando, seoGenerando, geoGenerando, fetchArticulos, generarSEO, generarGEO } = useAgentes()

const errorMsg = ref<string | null>(null)
const mensajeSEO = ref<string | null>(null)
const mensajeGEO = ref<string | null>(null)

// ── KPIs ───────────────────────────────────────────────────────────────────────

const articulosPublicados = computed(() =>
  articulos.value.filter(a => a.publicado).length
)

const ultimaFecha = computed(() => {
  if (articulos.value.length === 0) return 'Sin artículos'
  const mas_reciente = articulos.value.reduce((a, b) =>
    new Date(a.created_at) > new Date(b.created_at) ? a : b
  )
  return formatFecha(mas_reciente.created_at)
})

const ultimoAutor = computed(() => {
  if (articulos.value.length === 0) return null
  const mas_reciente = articulos.value.reduce((a, b) =>
    new Date(a.created_at) > new Date(b.created_at) ? a : b
  )
  return mas_reciente.autor_agente
})

// ── Acciones ───────────────────────────────────────────────────────────────────

async function cargar() {
  errorMsg.value = null
  try {
    await fetchArticulos({ limit: 10 })
  } catch (e: any) {
    errorMsg.value = e?.data?.detail ?? e?.message ?? 'Error al cargar artículos'
  }
}

async function accionGenerarSEO() {
  mensajeSEO.value = null
  errorMsg.value = null
  try {
    const res = await generarSEO()
    mensajeSEO.value = `Artículo encolado — task_id: ${res.task_id}`
    // Recargar lista tras un breve delay para reflejar posible nuevo artículo
    setTimeout(cargar, 3000)
  } catch (e: any) {
    errorMsg.value = e?.data?.detail ?? e?.message ?? 'Error al generar artículo SEO'
  }
}

async function accionGenerarGEO() {
  mensajeGEO.value = null
  errorMsg.value = null
  try {
    const res = await generarGEO()
    mensajeGEO.value = `Contenido GEO encolado — task_id: ${res.task_id}`
  } catch (e: any) {
    errorMsg.value = e?.data?.detail ?? e?.message ?? 'Error al generar contenido GEO'
  }
}

function abrirArticulo(slug: string) {
  window.open(`/blog/${slug}`, '_blank', 'noopener,noreferrer')
}

// ── Utilidades ─────────────────────────────────────────────────────────────────

function truncar(texto: string, max: number): string {
  if (!texto) return ''
  return texto.length <= max ? texto : texto.slice(0, max) + '…'
}

function formatFecha(iso: string): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

onMounted(cargar)
</script>
