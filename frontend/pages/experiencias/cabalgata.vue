<template>
  <div>

    <!-- HERO -->
    <section
      class="relative h-[420px] flex flex-col items-center justify-center bg-cover bg-center"
      style="background-image: url('/img/cabalgata-cresta-valle.jpg')"
    >
      <div class="absolute inset-0 bg-tierra-800/65"></div>
      <div class="relative z-10 container-site px-4 text-center">
        <NuxtLink to="/experiencias" class="inline-flex items-center gap-2 text-white/70 hover:text-white text-sm mb-6 transition-colors">
          ← Todas las experiencias
        </NuxtLink>
        <span class="block mb-4 px-4 py-1.5 rounded-full border border-dorado-400/70 bg-black/30 text-dorado-400 text-sm font-medium tracking-wide w-fit mx-auto">
          🐴 Aventura
        </span>
        <h1 class="font-display text-4xl md:text-5xl font-bold text-white leading-tight max-w-3xl mx-auto">
          Cabalgata por los Cerros del Tolima
        </h1>
        <p class="mt-4 text-white/85 text-lg max-w-2xl mx-auto leading-relaxed">
          Tres horas a caballo por los cerros más verdes del Tolima. Sin itinerarios fijos, sin grupos masivos.
        </p>
      </div>
    </section>

    <!-- CONTENIDO PRINCIPAL -->
    <section class="section-py bg-crema-50">
      <div class="container-site px-4">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">

          <!-- Descripción larga -->
          <div class="lg:col-span-2 space-y-8">

            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">La experiencia</h2>
              <div class="prose prose-tierra max-w-none text-gray-600 leading-relaxed space-y-4">
                <p>
                  Desde la hacienda, los senderos suben por colinas de pasto verde hasta miradores donde el Valle del Magdalena se abre frente a ti sin ningún obstáculo. En temporada seca, los cerros se ven hasta Mariquita. En temporada de lluvias, la niebla baja y convierte el recorrido en algo completamente diferente.
                </p>
                <p>
                  Los caballos de La Carmelita son criollos colombianos, acostumbrados al terreno. No importa si nunca has montado — el guía de la finca lleva más de 20 años en estos senderos y adapta el recorrido al grupo.
                </p>
                <p>
                  En el mirador, si el día está despejado, verás el Nevado del Tolima. Si tienes suerte y el tiempo acompaña, también el Nevado del Ruiz al norte. El mirador tiene las esculturas de la jirafa y el elefante: el lugar más fotografiado de toda la hacienda.
                </p>
              </div>
            </div>

            <!-- Galería de fotos -->
            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">Galería</h2>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                <img src="/img/cabalgata-grupo-mirador.jpg" alt="Grupo en el mirador" class="rounded-xl h-40 w-full object-cover" />
                <img src="/img/cabalgata-trail-valle.jpg" alt="Sendero hacia el valle" class="rounded-xl h-40 w-full object-cover" />
                <img src="/img/cabalgata-colinas-verdes.jpg" alt="Colinas verdes del Tolima" class="rounded-xl h-40 w-full object-cover" />
                <img src="/img/cabalgata-sendero-rio.jpg" alt="Sendero junto al río" class="rounded-xl h-40 w-full object-cover" />
                <img src="/img/mirador-jirafa-elefante-grupo.jpg" alt="Mirador con esculturas" class="rounded-xl h-40 w-full object-cover" />
                <img src="/img/nina-caballo-hacienda.jpg" alt="Niña a caballo en la hacienda" class="rounded-xl h-40 w-full object-cover" />
              </div>
            </div>

            <!-- Lo que incluye -->
            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">Qué incluye</h2>
              <ul class="space-y-3">
                <li v-for="item in incluye" :key="item" class="flex items-start gap-3 text-gray-600">
                  <span class="text-dorado-500 font-bold text-lg leading-tight">✓</span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>

            <!-- Preguntas frecuentes -->
            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">Preguntas frecuentes</h2>
              <div class="space-y-4">
                <div v-for="faq in faqs" :key="faq.q" class="border border-tierra-100 rounded-xl p-5 bg-white">
                  <p class="font-semibold text-tierra-800 mb-2">{{ faq.q }}</p>
                  <p class="text-gray-600 text-sm leading-relaxed">{{ faq.a }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Sidebar de reserva -->
          <div class="lg:col-span-1">
            <div class="sticky top-6 bg-white rounded-2xl border border-tierra-100 shadow-sm p-6 space-y-5">
              <h3 class="font-display text-xl font-bold text-tierra-800">Reservar</h3>

              <div class="space-y-3">
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <span class="text-dorado-500 text-base">⏱</span>
                  <span>3 a 4 horas</span>
                </div>
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <span class="text-dorado-500 text-base">👥</span>
                  <span>1 a 18 personas</span>
                </div>
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <span class="text-dorado-500 text-base">📊</span>
                  <span>Nivel: Fácil — Moderado</span>
                </div>
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <span class="text-dorado-500 text-base">🗓️</span>
                  <span>Disponible todos los días</span>
                </div>
              </div>

              <div class="border-t border-tierra-100 pt-4">
                <p class="text-sm text-gray-500 mb-1">Precio por persona</p>
                <p class="font-display text-3xl font-bold text-tierra-800">$80.000 <span class="text-base font-normal text-gray-500">COP</span></p>
                <p class="text-xs text-gray-400 mt-1">Incluido en paquetes Premium y Superior</p>
              </div>

              <NuxtLink
                to="/reservar"
                class="block text-center w-full px-6 py-4 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-bold text-base transition-colors"
              >
                Reservar estadía + cabalgata
              </NuxtLink>

              <a
                href="https://wa.me/573001234567?text=Hola%2C+quiero+información+sobre+la+cabalgata+en+La+Carmelita"
                target="_blank"
                class="block text-center w-full px-6 py-3 rounded-xl border border-tierra-200 hover:bg-tierra-50 text-tierra-800 font-semibold text-sm transition-colors"
              >
                💬 Preguntar por WhatsApp
              </a>
            </div>
          </div>

        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Cabalgata por los Cerros del Tolima — Hacienda La Carmelita',
  description: 'Recorre a caballo los cerros del Tolima y llega al mirador con vista 360° del Valle del Magdalena. Ideal para todas las edades. Hacienda La Carmelita, Lérida, Tolima.'
})

const incluye = [
  'Guía local experto en los senderos de la hacienda',
  'Caballo criollo colombiano adaptado al nivel del jinete',
  'Equipamiento completo: casco y chaleco de seguridad',
  'Hidratación durante todo el recorrido',
  'Parada en el mirador de las esculturas (jirafa y elefante)',
  'Fotos del recorrido compartidas por WhatsApp',
]

const faqs = [
  {
    q: '¿Se necesita experiencia previa montando a caballo?',
    a: 'No. Los caballos de La Carmelita son dóciles y el guía adapta el ritmo al grupo. Hemos tenido jinetes primerizos de 6 años y abuelos de 75.',
  },
  {
    q: '¿Hay límite de edad o peso?',
    a: 'Recomendamos que los menores de 6 años vayan acompañados por un adulto en el mismo caballo. No hay límite de peso pero sí pedimos informarlo al reservar.',
  },
  {
    q: '¿Qué pasa si llueve?',
    a: 'Las cabalgatas se hacen con llovizna leve. Si hay lluvia fuerte, se reagenda para el día siguiente o se ofrece otra actividad. La seguridad del jinete es primero.',
  },
  {
    q: '¿Puedo reservar solo la cabalgata sin estadía?',
    a: 'La cabalgata está incluida en los paquetes de estadía. Si quieres solo la actividad, escríbenos por WhatsApp y lo coordinamos.',
  },
]
</script>
