<template>
  <div>

    <!-- 404 inline -->
    <section v-if="!cargando && articulo === null" class="section-py bg-crema-50 min-h-[60vh] flex items-center justify-center">
      <div class="text-center max-w-md mx-auto px-4">
        <p class="text-6xl font-display font-bold text-tierra-100 mb-4">404</p>
        <h1 class="font-display text-2xl font-bold text-tierra-800 mb-3">Artículo no encontrado</h1>
        <p class="text-gray-600 mb-8">El artículo que buscas no existe o fue eliminado.</p>
        <NuxtLink
          to="/blog"
          class="inline-block px-6 py-3 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-semibold transition-colors"
        >
          Volver al blog
        </NuxtLink>
      </div>
    </section>

    <!-- Skeleton de carga -->
    <template v-else-if="cargando">
      <section class="section-py bg-crema-50">
        <div class="container-site px-4 max-w-4xl mx-auto">
          <div class="animate-pulse space-y-4">
            <div class="h-4 bg-tierra-100 rounded w-48" />
            <div class="h-8 bg-tierra-100 rounded w-3/4" />
            <div class="h-4 bg-tierra-100 rounded w-56" />
            <div class="h-6 bg-tierra-100 rounded w-full" />
            <div class="h-6 bg-tierra-100 rounded w-5/6" />
          </div>
        </div>
      </section>
    </template>

    <!-- Artículo completo -->
    <template v-else-if="articulo">

      <!-- ============================================================
           HERO DEL ARTÍCULO
      ============================================================ -->
      <section class="section-py bg-crema-50">
        <div class="container-site px-4 max-w-4xl mx-auto">

          <!-- Breadcrumb -->
          <nav class="flex items-center gap-2 text-xs text-gray-500 mb-6 flex-wrap">
            <NuxtLink to="/" class="hover:text-tierra-700 transition-colors">Inicio</NuxtLink>
            <span>→</span>
            <NuxtLink to="/blog" class="hover:text-tierra-700 transition-colors">Blog</NuxtLink>
            <span>→</span>
            <span class="text-tierra-700 font-medium truncate max-w-xs">{{ titulo }}</span>
          </nav>

          <!-- Badge de categoría -->
          <div class="mb-4">
            <span
              v-if="articulo.palabras_clave?.length"
              class="inline-block px-3 py-1.5 rounded-full bg-tierra-100 text-tierra-700 text-xs font-semibold"
            >
              {{ capitalizarPrimeraPalabra(articulo.palabras_clave[0]) }}
            </span>
          </div>

          <!-- Título -->
          <h1 class="font-display text-3xl md:text-4xl lg:text-5xl font-bold text-tierra-800 leading-tight mb-5">
            {{ titulo }}
          </h1>

          <!-- Meta: fecha + autor -->
          <div class="flex items-center gap-3 text-sm text-gray-500 mb-6 flex-wrap">
            <span v-if="articulo.fecha_publicacion || articulo.created_at">
              {{ formatFecha(articulo.fecha_publicacion ?? articulo.created_at) }}
            </span>
            <span class="text-tierra-200">|</span>
            <span>por {{ articulo.autor_agente ?? 'Agente SEO' }}</span>
          </div>

          <!-- Resumen -->
          <p
            v-if="resumen"
            class="text-gray-600 text-lg leading-relaxed max-w-2xl"
          >
            {{ resumen }}
          </p>

        </div>
      </section>

      <!-- ============================================================
           CONTENIDO + SIDEBAR
      ============================================================ -->
      <section class="section-py bg-white">
        <div class="container-site px-4 max-w-5xl mx-auto">
          <div class="flex gap-12 items-start">

            <!-- Cuerpo del artículo -->
            <article class="max-w-3xl mx-auto w-full md:flex-1 min-w-0">
              <div
                class="prose prose-lg prose-tierra max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap"
                v-html="contenidoHtml"
              />
            </article>

            <!-- Sidebar sticky (md+) -->
            <aside class="hidden md:block w-64 flex-shrink-0 sticky top-8">

              <!-- Palabras clave -->
              <div
                v-if="articulo.palabras_clave?.length"
                class="bg-crema-50 rounded-2xl border border-tierra-100 p-5 mb-5"
              >
                <h3 class="font-semibold text-tierra-800 text-sm mb-3">Temas relacionados</h3>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="kw in articulo.palabras_clave"
                    :key="kw"
                    class="px-2.5 py-1 rounded-full bg-white border border-tierra-100 text-tierra-700 text-xs font-medium"
                  >
                    {{ kw }}
                  </span>
                </div>
              </div>

              <!-- Schema markup badge -->
              <div
                v-if="articulo.schema_markup"
                class="bg-crema-50 rounded-2xl border border-tierra-100 p-5 mb-5"
              >
                <div class="flex items-center gap-2">
                  <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-green-100 text-green-700 text-xs font-semibold">
                    <span>✓</span> Structured data
                  </span>
                </div>
                <p class="text-xs text-gray-500 mt-2">Este artículo incluye Schema markup para buscadores.</p>
              </div>

              <!-- CTA reserva -->
              <div class="bg-tierra-800 rounded-2xl p-5 text-white">
                <h3 class="font-display font-bold text-lg mb-2 leading-snug">¿Te anima?</h3>
                <p class="text-tierra-100 text-sm mb-4 leading-relaxed">
                  Reserva tu estadía y vive la experiencia en La Carmelita.
                </p>
                <NuxtLink
                  to="/reservar"
                  class="inline-block w-full text-center px-4 py-2.5 rounded-xl bg-dorado-600 hover:bg-dorado-700 text-white font-semibold text-sm transition-colors"
                >
                  Reserva tu estadía
                </NuxtLink>
              </div>

            </aside>

          </div>
        </div>
      </section>

      <!-- CTA mobile (solo visible en móvil) -->
      <section class="section-py bg-tierra-50 md:hidden">
        <div class="container-site px-4 text-center max-w-sm mx-auto">
          <h2 class="font-display text-2xl font-bold text-tierra-800 mb-3">¿Te anima?</h2>
          <p class="text-gray-600 mb-6">Reserva tu estadía y vive la experiencia en La Carmelita.</p>
          <NuxtLink
            to="/reservar"
            class="inline-block px-8 py-3 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-bold transition-colors"
          >
            Reservar estadía
          </NuxtLink>
        </div>
      </section>

    </template>

  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const slug = computed(() => route.params.slug as string)

const { fetchArticulo } = useAgentes()

const articulo = ref<import('~/composables/useAgentes').ArticuloBlog | null | undefined>(undefined)
const cargando = ref(true)

// ── Detección de idioma ────────────────────────────────────────────────────────

const idiomaEN = computed(() => {
  if (import.meta.server) return false
  return navigator.language?.toLowerCase().startsWith('en') ?? false
})

// ── Campos calculados ─────────────────────────────────────────────────────────

const titulo = computed(() => {
  if (!articulo.value) return ''
  return idiomaEN.value && articulo.value.titulo_en
    ? articulo.value.titulo_en
    : articulo.value.titulo_es
})

const resumen = computed(() => {
  if (!articulo.value) return ''
  return idiomaEN.value && articulo.value.resumen_en
    ? articulo.value.resumen_en
    : articulo.value.resumen_es ?? ''
})

const contenido = computed(() => {
  if (!articulo.value) return ''
  return idiomaEN.value && articulo.value.contenido_en
    ? articulo.value.contenido_en
    : articulo.value.contenido_es
})

/**
 * Renderiza markdown simple o devuelve el texto con saltos de línea preservados.
 * No hay librería `marked` instalada en el proyecto; se aplica un renderizado
 * básico de los patrones markdown más comunes para el contenido generado.
 */
const contenidoHtml = computed(() => {
  const texto = contenido.value
  if (!texto) return ''

  // Renderizado markdown básico (headings, bold, italic, listas, párrafos)
  let html = texto
    // Headings
    .replace(/^### (.+)$/gm, '<h3 class="text-xl font-bold text-tierra-800 mt-6 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-2xl font-bold text-tierra-800 mt-8 mb-3">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-3xl font-bold text-tierra-800 mt-8 mb-4">$1</h1>')
    // Bold y italic
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Listas no ordenadas
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    // Listas ordenadas
    .replace(/^\d+\. (.+)$/gm, '<li class="ml-4 list-decimal">$1</li>')
    // Párrafos (líneas vacías)
    .replace(/\n\n/g, '</p><p class="mb-4">')

  // Envolver en párrafo inicial
  html = `<p class="mb-4">${html}</p>`

  // Agrupar lis consecutivos
  html = html.replace(/(<li[^>]*>.*?<\/li>\s*)+/gs, (match) => {
    const esOrdenada = match.includes('list-decimal')
    const tag = esOrdenada ? 'ol' : 'ul'
    return `<${tag} class="mb-4 space-y-1">${match}</${tag}>`
  })

  return html
})

// ── SEO ───────────────────────────────────────────────────────────────────────

useSeoMeta({
  title: computed(() =>
    articulo.value
      ? `${articulo.value.titulo_es} — Hacienda La Carmelita`
      : 'Blog — Hacienda La Carmelita'
  ),
  description: computed(() => articulo.value?.meta_descripcion_es ?? ''),
})

// ── Schema markup ──────────────────────────────────────────────────────────────

useHead(computed(() => {
  if (!articulo.value?.schema_markup) return {}
  return {
    script: [
      {
        type: 'application/ld+json',
        children: JSON.stringify(articulo.value.schema_markup),
      },
    ],
  }
}))

// ── Utilidades ─────────────────────────────────────────────────────────────────

function capitalizarPrimeraPalabra(texto: string): string {
  if (!texto) return ''
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

function formatFecha(iso: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// ── Carga del artículo ────────────────────────────────────────────────────────

onMounted(async () => {
  cargando.value = true
  articulo.value = await fetchArticulo(slug.value)
  cargando.value = false
})
</script>
