<template>
  <div>

    <!-- ============================================================
         HERO — ~400px con foto de fondo
    ============================================================ -->
    <section
      class="relative h-[400px] flex flex-col items-center justify-center bg-cover bg-center"
      style="background-image: url('/img/cabalgata-cresta-valle.jpg')"
    >
      <div class="absolute inset-0 bg-tierra-800/70"></div>
      <div class="relative z-10 container-site px-4 text-center">
        <span class="inline-block mb-4 px-4 py-1.5 rounded-full border border-dorado-400/70 bg-black/30 text-dorado-400 text-sm font-medium tracking-wide">
          🐴 Nuestras Experiencias
        </span>
        <h1 class="font-display text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight max-w-4xl mx-auto">
          Experiencias en La Carmelita
        </h1>
        <p class="mt-5 text-white/85 text-lg max-w-3xl mx-auto leading-relaxed">
          Aquí no hay itinerarios de hotel ni paquetes armados por un computador. Cada experiencia en La Carmelita nació de la tierra misma, de los animales, de las personas que han vivido estos campos por generaciones.
        </p>
      </div>
    </section>

    <!-- ============================================================
         GRID DE EXPERIENCIAS — 5 cards
    ============================================================ -->
    <section class="section-py bg-crema-50">
      <div class="container-site px-4">

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

          <!-- Card 1 — Cabalgata por los Cerros del Tolima -->
          <div class="bg-white rounded-2xl border border-tierra-100 shadow-sm overflow-hidden flex flex-col">
            <NuxtLink to="/experiencias/cabalgata" class="relative h-56 overflow-hidden block">
              <img
                src="/img/cabalgata-grupo-mirador.jpg"
                alt="Grupo de jinetes en el mirador de La Carmelita"
                class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
              />
              <span class="absolute top-3 left-3 px-3 py-1 rounded-full bg-tierra-800/85 text-white text-xs font-semibold backdrop-blur-sm">
                🐴 Aventura
              </span>
            </NuxtLink>
            <div class="p-6 flex flex-col flex-1">
              <h2 class="font-display text-xl font-bold text-tierra-800 mb-3">
                <NuxtLink to="/experiencias/cabalgata" class="hover:text-tierra-600 transition-colors">
                  Cabalgata por los Cerros del Tolima
                </NuxtLink>
              </h2>
              <div class="flex flex-wrap gap-2 mb-4">
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-tierra-50 border border-tierra-100 text-tierra-700 text-xs font-medium">
                  ⏱ 3 a 4 horas
                </span>
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-dorado-50 border border-dorado-200 text-dorado-700 text-xs font-medium">
                  💰 $80.000 COP / persona
                </span>
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-tierra-50 border border-tierra-100 text-tierra-700 text-xs font-medium">
                  📊 Fácil - Moderado
                </span>
              </div>
              <p class="text-gray-600 leading-relaxed text-sm mb-4 flex-1">
                Recorre a caballo las colinas verdes que rodean la hacienda y descubre paisajes del Tolima que muy pocos colombianos han visto de cerca. Una aventura accesible para toda la familia.
              </p>
              <div class="mb-5">
                <p class="text-xs font-semibold text-tierra-700 uppercase tracking-wide mb-2">Qué incluye:</p>
                <ul class="space-y-1">
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Guía local experto en los senderos de la hacienda
                  </li>
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Equipamiento completo (casco, chaleco de seguridad)
                  </li>
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Hidratación durante el recorrido
                  </li>
                </ul>
              </div>
              <div class="flex gap-3 mt-auto">
                <NuxtLink
                  to="/experiencias/cabalgata"
                  class="flex-1 block text-center px-4 py-3 rounded-xl border border-tierra-200 hover:bg-tierra-50 text-tierra-800 font-semibold text-sm transition-colors"
                >
                  Ver detalles
                </NuxtLink>
                <NuxtLink
                  to="/reservar"
                  class="flex-1 block text-center px-4 py-3 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-semibold text-sm transition-colors"
                >
                  Reservar
                </NuxtLink>
              </div>
            </div>
          </div>

          <!-- Card 2 — Cena a la Leña -->
          <div class="bg-white rounded-2xl border border-tierra-100 shadow-sm overflow-hidden flex flex-col">
            <NuxtLink to="/experiencias/cena-lena" class="relative h-56 overflow-hidden block">
              <img
                src="/img/gastronomia-bbq-parrilla.jpg"
                alt="BBQ con carne y verduras a la parrilla en La Carmelita"
                class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
              />
              <span class="absolute top-3 left-3 px-3 py-1 rounded-full bg-tierra-800/85 text-white text-xs font-semibold backdrop-blur-sm">
                🍖 Gastronomía
              </span>
            </NuxtLink>
            <div class="p-6 flex flex-col flex-1">
              <h2 class="font-display text-xl font-bold text-tierra-800 mb-3">
                <NuxtLink to="/experiencias/cena-lena" class="hover:text-tierra-600 transition-colors">
                  Cena a la Leña — BBQ Bajo las Estrellas del Tolima
                </NuxtLink>
              </h2>
              <div class="flex flex-wrap gap-2 mb-4">
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-dorado-50 border border-dorado-200 text-dorado-700 text-xs font-medium">
                  💰 $120.000 COP / persona
                </span>
              </div>
              <p class="text-gray-600 leading-relaxed text-sm mb-4 flex-1">
                Cortes premium cocinados a fuego de leña en los jardines centenarios de la hacienda. Una cena que huele a campo, sabe a Colombia y se disfruta bajo un cielo sin contaminación lumínica.
              </p>
              <div class="mb-5">
                <p class="text-xs font-semibold text-tierra-700 uppercase tracking-wide mb-2">Qué incluye:</p>
                <ul class="space-y-1">
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Cortes premium de res a la parrilla de leña
                  </li>
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Acompañamientos de temporada y salsas artesanales
                  </li>
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Servicio de mesa en los jardines
                  </li>
                </ul>
              </div>
              <div class="flex gap-3 mt-auto">
                <NuxtLink
                  to="/experiencias/cena-lena"
                  class="flex-1 block text-center px-4 py-3 rounded-xl border border-tierra-200 hover:bg-tierra-50 text-tierra-800 font-semibold text-sm transition-colors"
                >
                  Ver detalles
                </NuxtLink>
                <NuxtLink
                  to="/reservar"
                  class="flex-1 block text-center px-4 py-3 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-semibold text-sm transition-colors"
                >
                  Reservar
                </NuxtLink>
              </div>
            </div>
          </div>

          <!-- Card 3 — Tour del Arroz -->
          <div class="bg-white rounded-2xl border border-tierra-100 shadow-sm overflow-hidden flex flex-col">
            <NuxtLink to="/experiencias/tour-arrocero" class="relative h-56 overflow-hidden block">
              <img
                src="/img/arrozales-tolima.jpg"
                alt="Arrozales del Tolima con cielo azul"
                class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
              />
              <span class="absolute top-3 left-3 px-3 py-1 rounded-full bg-tierra-800/85 text-white text-xs font-semibold backdrop-blur-sm">
                🌾 Cultura
              </span>
            </NuxtLink>
            <div class="p-6 flex flex-col flex-1">
              <h2 class="font-display text-xl font-bold text-tierra-800 mb-3">
                <NuxtLink to="/experiencias/tour-arrocero" class="hover:text-tierra-600 transition-colors">
                  Tour del Arroz — En el Origen de una Tradición
                </NuxtLink>
              </h2>
              <div class="flex flex-wrap gap-2 mb-4">
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-tierra-50 border border-tierra-100 text-tierra-700 text-xs font-medium">
                  ⏱ 2 horas
                </span>
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-dorado-50 border border-dorado-200 text-dorado-700 text-xs font-medium">
                  💰 $45.000 COP / persona
                </span>
              </div>
              <p class="text-gray-600 leading-relaxed text-sm mb-4 flex-1">
                Camina entre los arrozales de Lérida y aprende de primera mano cómo nació la industria que convirtió al Tolima en la despensa arrocera de Colombia.
              </p>
              <div class="mb-5">
                <p class="text-xs font-semibold text-tierra-700 uppercase tracking-wide mb-2">Qué incluye:</p>
                <ul class="space-y-1">
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Recorrido guiado por los arrozales
                  </li>
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Explicación del proceso de cultivo
                  </li>
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Degustación de productos artesanales de la región
                  </li>
                </ul>
              </div>
              <div class="flex gap-3 mt-auto">
                <NuxtLink
                  to="/experiencias/tour-arrocero"
                  class="flex-1 block text-center px-4 py-3 rounded-xl border border-tierra-200 hover:bg-tierra-50 text-tierra-800 font-semibold text-sm transition-colors"
                >
                  Ver detalles
                </NuxtLink>
                <NuxtLink
                  to="/reservar"
                  class="flex-1 block text-center px-4 py-3 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-semibold text-sm transition-colors"
                >
                  Reservar
                </NuxtLink>
              </div>
            </div>
          </div>

          <!-- Card 4 — Retiro Privado -->
          <div class="bg-white rounded-2xl border border-tierra-100 shadow-sm overflow-hidden flex flex-col">
            <NuxtLink to="/experiencias/retiro-privado" class="relative h-56 overflow-hidden block">
              <img
                src="/img/cabalgata-arbol-centenario.jpg"
                alt="Jinetes bajo árbol centenario en La Carmelita"
                class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
              />
              <span class="absolute top-3 left-3 px-3 py-1 rounded-full bg-tierra-800/85 text-white text-xs font-semibold backdrop-blur-sm">
                ❤️ Romance
              </span>
            </NuxtLink>
            <div class="p-6 flex flex-col flex-1">
              <h2 class="font-display text-xl font-bold text-tierra-800 mb-3">
                <NuxtLink to="/experiencias/retiro-privado" class="hover:text-tierra-600 transition-colors">
                  Retiro Privado — La Carmelita Solo para Ustedes Dos
                </NuxtLink>
              </h2>
              <div class="flex flex-wrap gap-2 mb-4">
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-dorado-50 border border-dorado-200 text-dorado-700 text-xs font-medium">
                  💰 Desde $1.200.000 COP / noche
                </span>
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-tierra-50 border border-tierra-100 text-tierra-700 text-xs font-medium">
                  ⏱ Mínimo 2 noches
                </span>
              </div>
              <p class="text-gray-600 leading-relaxed text-sm mb-4 flex-1">
                Dos noches en la hacienda reservada exclusivamente para ustedes, con decoración romántica, cena privada a la leña y el silencio absoluto del campo tolimense.
              </p>
              <div class="mb-5">
                <p class="text-xs font-semibold text-tierra-700 uppercase tracking-wide mb-2">Qué incluye:</p>
                <ul class="space-y-1">
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Hacienda reservada solo para la pareja
                  </li>
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Decoración romántica personalizada
                  </li>
                  <li class="flex items-start gap-2 text-sm text-gray-600">
                    <span class="text-dorado-500 mt-0.5">✓</span> Cena privada a la leña la primera noche
                  </li>
                </ul>
              </div>
              <div class="flex gap-3 mt-auto">
                <NuxtLink
                  to="/experiencias/retiro-privado"
                  class="flex-1 block text-center px-4 py-3 rounded-xl border border-tierra-200 hover:bg-tierra-50 text-tierra-800 font-semibold text-sm transition-colors"
                >
                  Ver detalles
                </NuxtLink>
                <NuxtLink
                  to="/reservar"
                  class="flex-1 block text-center px-4 py-3 rounded-xl bg-dorado-500 hover:bg-dorado-600 text-white font-semibold text-sm transition-colors"
                >
                  Reservar
                </NuxtLink>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ============================================================
         CTA FINAL
    ============================================================ -->
    <section class="section-py bg-tierra-50">
      <div class="container-site px-4 text-center max-w-2xl mx-auto">
        <div class="text-5xl mb-4">🎯</div>
        <h2 class="font-display text-3xl md:text-4xl font-bold text-tierra-800 mb-4">
          ¿Quieres combinar varias experiencias?
        </h2>
        <p class="text-gray-600 text-lg leading-relaxed mb-8">
          Contáctanos y armamos el plan perfecto para tu grupo.
        </p>
        <NuxtLink
          to="/chat"
          class="inline-block px-8 py-4 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-bold text-base shadow-lg transition-colors"
        >
          Hablar con Carmelita (IA)
        </NuxtLink>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Experiencias — Hacienda La Carmelita',
  description: 'Cabalgatas, mirador de esculturas, tour del arroz, cena a la leña y retiro privado en Lérida, Tolima. Experiencias auténticas en la hacienda colombiana más exclusiva del Tolima.'
})
</script>
