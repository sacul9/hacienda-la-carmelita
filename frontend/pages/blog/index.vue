<template>
  <div>

    <!-- ============================================================
         HEADER DE PÁGINA
    ============================================================ -->
    <section class="section-py bg-crema-50">
      <div class="container-site px-4 text-center max-w-2xl mx-auto">
        <span class="inline-block mb-4 px-4 py-1.5 rounded-full bg-tierra-100 text-tierra-700 text-sm font-medium">
          Historias del campo
        </span>
        <h1 class="font-display text-4xl md:text-5xl font-bold text-tierra-800 leading-tight">
          Historias desde La Carmelita
        </h1>
        <p class="mt-5 text-gray-600 text-lg leading-relaxed">
          Relatos del campo, del Tolima y del arte de viajar despacio.
        </p>
      </div>
    </section>

    <!-- ============================================================
         GRID DE BLOG CARDS — hasta 3 artículos o skeletons
    ============================================================ -->
    <section class="section-py bg-white">
      <div class="container-site px-4">

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">

          <!-- Estado de carga: 3 skeleton cards -->
          <template v-if="articuloCargando">
            <div
              v-for="n in 3"
              :key="n"
              class="animate-pulse bg-tierra-100 rounded-2xl h-80"
            />
          </template>

          <!-- Artículos dinámicos -->
          <template v-else>
            <NuxtLink
              v-for="articulo in articulos.slice(0, 3)"
              :key="articulo.id"
              :to="`/blog/${articulo.slug}`"
              class="bg-white rounded-2xl border border-tierra-100 shadow-sm overflow-hidden flex flex-col cursor-pointer group hover:shadow-md transition-shadow"
            >
              <div class="relative h-56 overflow-hidden">
                <img
                  src="/img/blog-default.jpg"
                  :alt="articulo.titulo_es"
                  class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <span class="absolute top-3 left-3 px-3 py-1 rounded-full bg-white/90 text-tierra-700 text-xs font-semibold backdrop-blur-sm">
                  {{ capitalizarPrimeraPalabra(articulo.palabras_clave?.[0] ?? 'Historia y Cultura') }}
                </span>
              </div>
              <div class="p-6 flex flex-col flex-1">
                <h2 class="font-display text-xl font-bold text-tierra-800 mb-3 leading-snug group-hover:text-tierra-600 transition-colors">
                  {{ articulo.titulo_es }}
                </h2>
                <p class="text-gray-600 text-sm leading-relaxed flex-1 mb-5">
                  {{ articulo.resumen_es ?? articulo.contenido_es.slice(0, 200) + '…' }}
                </p>
                <span class="inline-flex items-center text-dorado-600 font-semibold text-sm group-hover:text-dorado-700 transition-colors">
                  Leer más <span class="ml-1">→</span>
                </span>
              </div>
            </NuxtLink>

            <!-- Si la API no retorna artículos, mostrar mensaje discreto -->
            <div
              v-if="articulos.length === 0"
              class="col-span-3 py-12 text-center text-gray-400"
            >
              <p>Próximamente más historias desde el campo.</p>
            </div>
          </template>

        </div>

      </div>
    </section>

    <!-- ============================================================
         CTA — al final del blog
    ============================================================ -->
    <section class="section-py bg-tierra-50">
      <div class="container-site px-4 text-center max-w-2xl mx-auto">
        <h2 class="font-display text-3xl font-bold text-tierra-800 mb-4">
          ¿Listo para vivir la historia en primera persona?
        </h2>
        <p class="text-gray-600 text-lg leading-relaxed mb-8">
          Todo lo que lees aquí lo puedes vivir. Reserva tu estadía en La Carmelita y llévate el relato propio.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <NuxtLink
            to="/reservar"
            class="inline-block px-8 py-4 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-bold text-base shadow-lg transition-colors"
          >
            Reservar estadía
          </NuxtLink>
          <NuxtLink
            to="/experiencias"
            class="inline-block px-8 py-4 rounded-xl border-2 border-tierra-800 text-tierra-800 hover:bg-tierra-50 font-bold text-base transition-colors"
          >
            Ver experiencias
          </NuxtLink>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Blog — Hacienda La Carmelita',
  description: 'Historias desde La Carmelita: la historia del arroz de Lérida, cabalgatas por el Tolima y consejos para escapadas familiares rurales. Relatos del campo colombiano.',
})

const { fetchArticulos, articulos, articuloCargando } = useAgentes()

function capitalizarPrimeraPalabra(texto: string): string {
  if (!texto) return 'Historia y Cultura'
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

onMounted(() => fetchArticulos({ limit: 3 }))
</script>
