<template>
  <div>

    <!-- ============================================================
         1. HERO — Full screen con foto de fondo
    ============================================================ -->
    <section
      class="relative min-h-screen flex flex-col items-center justify-center bg-cover bg-center"
      style="background-image: url('/img/hacienda-exterior-piscina.jpg')"
    >
      <!-- Overlay oscuro ~40% -->
      <div class="absolute inset-0 bg-black/45"></div>

      <!-- Contenido -->
      <div class="relative z-10 container-site text-center px-4">
        <!-- Badge -->
        <span class="inline-block mb-6 px-4 py-1.5 rounded-full border border-dorado-400/70 bg-black/30 text-dorado-400 text-sm font-medium tracking-wide">
          🌿 Lérida, Tolima · Colombia
        </span>

        <!-- Headline -->
        <h1 class="font-display text-4xl md:text-6xl lg:text-7xl text-white font-bold leading-tight max-w-5xl mx-auto">
          Donde el campo colombiano<br class="hidden md:block" /> te abraza de verdad
        </h1>

        <!-- Subtítulo -->
        <p class="mt-6 text-white/90 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
          Escápate al corazón del Tolima. Hacienda La Carmelita te recibe en Lérida — la cuna del arroz colombiano — con experiencias únicas, naturaleza pura y una exclusividad que muy pocos conocen.
        </p>

        <!-- CTAs -->
        <div class="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <NuxtLink
            to="/reservar"
            class="btn-primary inline-block px-8 py-4 rounded-xl font-semibold text-base bg-tierra-800 text-white hover:bg-tierra-900 transition-colors shadow-lg"
          >
            Reserva tu escapada
          </NuxtLink>
          <NuxtLink
            to="/experiencias"
            class="inline-block px-8 py-4 rounded-xl font-semibold text-base border-2 border-white text-white hover:bg-white/10 transition-colors"
          >
            Descubre las experiencias
          </NuxtLink>
        </div>
      </div>

      <!-- Scroll indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 animate-bounce">
        <svg class="w-8 h-8 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </section>

    <!-- ============================================================
         2. POR QUÉ ELEGIRNOS — 3 cards
    ============================================================ -->
    <section class="section-py bg-crema-50">
      <div class="container-site px-4">
        <div class="text-center max-w-2xl mx-auto mb-14">
          <h2 class="font-display text-3xl md:text-4xl font-bold text-tierra-800">
            Una hacienda hecha solo para ti
          </h2>
          <p class="mt-4 text-gray-600 text-lg">
            Tres razones que hacen de La Carmelita un lugar diferente a todo lo que has vivido
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Card 1 -->
          <div class="card card-hover rounded-2xl p-8 bg-white shadow-sm border border-tierra-100 text-center">
            <div class="text-5xl mb-5">🏡</div>
            <h3 class="font-display text-xl font-bold text-tierra-800 mb-3">Solo tu grupo, siempre</h3>
            <p class="text-gray-600 leading-relaxed">
              La hacienda es tuya. No compartimos instalaciones con extraños. Cuando llegas, la Carmelita te pertenece por completo — con su piscina, sus jardines y su silencio.
            </p>
          </div>

          <!-- Card 2 -->
          <div class="card card-hover rounded-2xl p-8 bg-white shadow-sm border border-tierra-100 text-center">
            <div class="text-5xl mb-5">🦒</div>
            <h3 class="font-display text-xl font-bold text-tierra-800 mb-3">El mirador que nadie olvida</h3>
            <p class="text-gray-600 leading-relaxed">
              Sube a caballo hasta nuestro mirador secreto y encuentra algo que no esperabas: esculturas de jirafa y elefante vigilando el Valle del Magdalena. Una vista de 360° que se queda grabada para siempre.
            </p>
          </div>

          <!-- Card 3 -->
          <div class="card card-hover rounded-2xl p-8 bg-white shadow-sm border border-tierra-100 text-center">
            <div class="text-5xl mb-5">🌾</div>
            <h3 class="font-display text-xl font-bold text-tierra-800 mb-3">La tierra donde nació el arroz colombiano</h3>
            <p class="text-gray-600 leading-relaxed">
              Lérida, Tolima, no es solo un municipio — es el origen de una tradición que alimenta al país. Aquí vivirás esa historia de primera mano, entre arrozales verdes y gente que la lleva en la sangre.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ============================================================
         3. FOTO DESTACADA — El mirador (full-width impactante)
    ============================================================ -->
    <section class="relative w-full h-[500px] md:h-[600px] overflow-hidden">
      <img
        src="/img/mirador-jirafa-elefante-grupo.jpg"
        alt="Mirador con esculturas de jirafa y elefante en Hacienda La Carmelita"
        class="absolute inset-0 w-full h-full object-cover object-center"
      />
      <!-- Overlay degradado -->
      <div class="absolute inset-0 bg-gradient-to-t from-tierra-900/80 via-tierra-900/30 to-transparent"></div>

      <!-- Texto encima -->
      <div class="absolute inset-0 flex flex-col items-center justify-end pb-14 px-4 text-center z-10">
        <span class="inline-block mb-4 px-3 py-1 rounded-full bg-dorado-500/90 text-white text-xs font-semibold tracking-widest uppercase">
          📍 Mirador de las Esculturas · La Carmelita
        </span>
        <h2 class="font-display text-3xl md:text-5xl font-bold text-white">
          El mirador que nadie olvida
        </h2>
        <p class="mt-3 text-white/85 text-lg max-w-xl">
          Jinetes, jirafas, elefantes y el Valle del Magdalena a tus pies. Solo aquí.
        </p>
      </div>
    </section>

    <!-- ============================================================
         4. STATS — 4 números grandes
    ============================================================ -->
    <section class="section-py bg-tierra-800">
      <div class="container-site px-4">
        <div class="text-center mb-12">
          <h2 class="font-display text-3xl md:text-4xl font-bold text-white">La Carmelita en cifras</h2>
          <p class="mt-3 text-tierra-200 text-lg">Ochenta años de historia, un solo grupo a la vez</p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <p class="text-5xl md:text-6xl font-bold text-dorado-400">120</p>
            <p class="mt-1 text-sm font-semibold text-dorado-400 uppercase tracking-wide">hectáreas</p>
            <p class="mt-2 text-tierra-200 text-sm leading-snug">de tierra viva en el corazón del Tolima</p>
          </div>
          <div>
            <p class="text-5xl md:text-6xl font-bold text-dorado-400">18</p>
            <p class="mt-1 text-sm font-semibold text-dorado-400 uppercase tracking-wide">huéspedes máx.</p>
            <p class="mt-2 text-tierra-200 text-sm leading-snug">toda la hacienda reservada solo para tu grupo</p>
          </div>
          <div>
            <p class="text-5xl md:text-6xl font-bold text-dorado-400">+80</p>
            <p class="mt-1 text-sm font-semibold text-dorado-400 uppercase tracking-wide">años de historia</p>
            <p class="mt-2 text-tierra-200 text-sm leading-snug">de tradición arrocera y vocación hospitalaria</p>
          </div>
          <div>
            <p class="text-5xl md:text-6xl font-bold text-dorado-400">5</p>
            <p class="mt-1 text-sm font-semibold text-dorado-400 uppercase tracking-wide">experiencias únicas</p>
            <p class="mt-2 text-tierra-200 text-sm leading-snug">diseñadas para reconectar con la tierra y con los tuyos</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ============================================================
         5. GALERÍA — Grid bento-style
    ============================================================ -->
    <section class="section-py bg-white">
      <div class="container-site px-4">
        <div class="text-center max-w-2xl mx-auto mb-12">
          <h2 class="font-display text-3xl md:text-4xl font-bold text-tierra-800">
            La Carmelita en imágenes
          </h2>
          <p class="mt-4 text-gray-600 text-lg">
            Algunas fotos lo muestran todo. Otras simplemente no alcanzan a transmitir lo que se siente estar aquí.
          </p>
        </div>

        <!-- Fila 1: 2/3 + 1/3 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div class="md:col-span-2 overflow-hidden rounded-2xl h-72 md:h-96 group">
            <img
              src="/img/cabalgata-cresta-valle.jpg"
              alt="Fila de jinetes por cresta verde con montañas al fondo"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
          <div class="overflow-hidden rounded-2xl h-72 md:h-96 group">
            <img
              src="/img/nina-caballo-hacienda.jpg"
              alt="Niña sonriente a caballo frente a la hacienda"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
        </div>

        <!-- Fila 2: 3 iguales -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="overflow-hidden rounded-2xl h-56 md:h-64 group">
            <img
              src="/img/piscina-familia.jpg"
              alt="Familia jugando en piscina cristalina"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
          <div class="overflow-hidden rounded-2xl h-56 md:h-64 group">
            <img
              src="/img/gastronomia-bbq-parrilla.jpg"
              alt="BBQ con cortes de carne a la parrilla"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
          <div class="overflow-hidden rounded-2xl h-56 md:h-64 group">
            <img
              src="/img/jardines-ninos-jugando.jpg"
              alt="Niños jugando fútbol bajo árboles centenarios"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- ============================================================
         6. TESTIMONIOS — 3 cards
    ============================================================ -->
    <section class="section-py bg-tierra-50">
      <div class="container-site px-4">
        <div class="text-center max-w-2xl mx-auto mb-14">
          <h2 class="font-display text-3xl md:text-4xl font-bold text-tierra-800">
            Lo que dicen quienes ya vivieron La Carmelita
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- T1 -->
          <div class="bg-white rounded-2xl p-8 shadow-sm border border-tierra-100 flex flex-col">
            <div class="text-5xl text-dorado-400 font-serif leading-none mb-4">"</div>
            <p class="text-gray-700 leading-relaxed flex-1">
              Llevamos a los niños sin saber muy bien qué esperar, y terminamos siendo nosotros los adultos quienes no queríamos irnos. Alimentar el ganado Brahman, ver los arrozales al atardecer, la piscina... La Carmelita le devuelve a uno algo que la ciudad se lleva sin que uno se dé cuenta.
            </p>
            <div class="mt-6 pt-6 border-t border-tierra-100">
              <p class="text-yellow-400 text-lg mb-1">⭐⭐⭐⭐⭐</p>
              <p class="font-semibold text-tierra-800">Sandra Morales</p>
              <p class="text-sm text-gray-500">Bogotá, D.C.</p>
            </div>
          </div>

          <!-- T2 -->
          <div class="bg-white rounded-2xl p-8 shadow-sm border border-tierra-100 flex flex-col">
            <div class="text-5xl text-dorado-400 font-serif leading-none mb-4">"</div>
            <p class="text-gray-700 leading-relaxed flex-1">
              Fuimos por nuestra primera cena de aniversario y volvemos cada año. El mirador con las esculturas de la jirafa y el elefante es de otro mundo — no lo creerías si no lo ves con tus propios ojos. La cena a la leña bajo las estrellas cerró la noche perfectamente.
            </p>
            <div class="mt-6 pt-6 border-t border-tierra-100">
              <p class="text-yellow-400 text-lg mb-1">⭐⭐⭐⭐⭐</p>
              <p class="font-semibold text-tierra-800">Andrés &amp; Valentina Restrepo</p>
              <p class="text-sm text-gray-500">Medellín, Antioquia</p>
            </div>
          </div>

          <!-- T3 -->
          <div class="bg-white rounded-2xl p-8 shadow-sm border border-tierra-100 flex flex-col">
            <div class="text-5xl text-dorado-400 font-serif leading-none mb-4">"</div>
            <p class="text-gray-700 leading-relaxed flex-1">
              Somos ocho amigos y buscábamos algo diferente a los mismos planes de siempre. La Carmelita nos sorprendió con todo: la cabalgata fue espectacular, el asado fue brutal, y tener la hacienda entera para nosotros solos no tiene precio. El próximo año repetimos, sí o sí.
            </p>
            <div class="mt-6 pt-6 border-t border-tierra-100">
              <p class="text-yellow-400 text-lg mb-1">⭐⭐⭐⭐⭐</p>
              <p class="font-semibold text-tierra-800">Sebastián Guerrero</p>
              <p class="text-sm text-gray-500">Cali, Valle del Cauca</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============================================================
         7. CTA FINAL — Banner de reserva con foto de fondo
    ============================================================ -->
    <section
      class="relative section-py bg-cover bg-center"
      style="background-image: url('/img/cabalgata-cresta-valle.jpg')"
    >
      <!-- Overlay tierra-800/80 -->
      <div class="absolute inset-0 bg-tierra-800/80"></div>

      <div class="relative z-10 container-site px-4 text-center">
        <h2 class="font-display text-3xl md:text-5xl font-bold text-white">
          Tu próxima escapada te está esperando
        </h2>
        <p class="mt-5 text-white/80 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
          Disponibilidad limitada. La hacienda recibe solo un grupo a la vez — asegura tus fechas antes de que alguien más lo haga.
        </p>
        <NuxtLink
          to="/reservar"
          class="mt-10 inline-block px-10 py-4 rounded-xl bg-dorado-500 hover:bg-dorado-600 text-white font-bold text-lg shadow-xl transition-colors"
        >
          Consultar disponibilidad y reservar
        </NuxtLink>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Hacienda La Carmelita — Lérida, Tolima',
  description: 'Escápate al corazón del Tolima. Hacienda La Carmelita: exclusividad total, cabalgatas al mirador con esculturas de jirafa y elefante, piscina, gastronomía y los arrozales de Lérida. Solo un grupo a la vez.'
})
</script>
