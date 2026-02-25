<template>
  <div>

    <!-- ============================================================
         HERO — 300px fondo tierra-800 sólido, sin foto
    ============================================================ -->
    <section class="relative h-[300px] flex flex-col items-center justify-center bg-tierra-800">
      <div class="container-site px-4 text-center">
        <h1 class="font-display text-4xl md:text-5xl font-bold text-white leading-tight max-w-3xl mx-auto">
          Lérida, Tolima — Más cerca de lo que imaginas
        </h1>
        <p class="mt-5 text-white/80 text-lg max-w-2xl mx-auto leading-relaxed">
          La Carmelita está en el corazón del norte del Tolima, rodeada de arrozales, cerros y el río Magdalena. Llegar es parte del viaje.
        </p>
      </div>
    </section>

    <!-- ============================================================
         CÓMO LLEGAR — 3 cards en fila
    ============================================================ -->
    <section class="section-py bg-crema-50">
      <div class="container-site px-4">

        <div class="text-center max-w-2xl mx-auto mb-12">
          <h2 class="font-display text-3xl md:text-4xl font-bold text-tierra-800">
            ¿Cómo llegar a La Carmelita?
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

          <!-- Bogotá -->
          <div class="bg-white rounded-2xl p-8 border border-tierra-100 shadow-sm hover:shadow-md transition-shadow">
            <div class="text-4xl mb-4">🚗</div>
            <h3 class="font-display text-xl font-bold text-tierra-800 mb-1">Desde Bogotá</h3>
            <div class="flex flex-wrap gap-2 mb-4 mt-3">
              <span class="px-3 py-1 rounded-full bg-tierra-50 border border-tierra-100 text-tierra-700 text-xs font-medium">
                ~210 km
              </span>
              <span class="px-3 py-1 rounded-full bg-dorado-50 border border-dorado-200 text-dorado-700 text-xs font-medium">
                3 a 3,5 horas
              </span>
            </div>
            <p class="text-gray-600 text-sm leading-relaxed">
              Toma la ruta Bogotá–Honda por la vía Villeta o la vía Girardot–Espinal–Lérida. El paisaje que se abre al bajar al Valle del Magdalena ya es parte del plan.
            </p>
          </div>

          <!-- Ibagué -->
          <div class="bg-white rounded-2xl p-8 border border-tierra-100 shadow-sm hover:shadow-md transition-shadow">
            <div class="text-4xl mb-4">✈️</div>
            <h3 class="font-display text-xl font-bold text-tierra-800 mb-1">Desde Ibagué</h3>
            <div class="flex flex-wrap gap-2 mb-4 mt-3">
              <span class="px-3 py-1 rounded-full bg-tierra-50 border border-tierra-100 text-tierra-700 text-xs font-medium">
                ~70 km
              </span>
              <span class="px-3 py-1 rounded-full bg-dorado-50 border border-dorado-200 text-dorado-700 text-xs font-medium">
                1 a 1,5 horas
              </span>
            </div>
            <p class="text-gray-600 text-sm leading-relaxed">
              Ruta directa por la vía Ibagué–Lérida. La opción más cómoda si se vuela al Aeropuerto Perales de Ibagué.
            </p>
          </div>

          <!-- Medellín -->
          <div class="bg-white rounded-2xl p-8 border border-tierra-100 shadow-sm hover:shadow-md transition-shadow">
            <div class="text-4xl mb-4">🚗</div>
            <h3 class="font-display text-xl font-bold text-tierra-800 mb-1">Desde Medellín</h3>
            <div class="flex flex-wrap gap-2 mb-4 mt-3">
              <span class="px-3 py-1 rounded-full bg-tierra-50 border border-tierra-100 text-tierra-700 text-xs font-medium">
                ~320 km
              </span>
              <span class="px-3 py-1 rounded-full bg-dorado-50 border border-dorado-200 text-dorado-700 text-xs font-medium">
                4,5 a 5 horas
              </span>
            </div>
            <p class="text-gray-600 text-sm leading-relaxed">
              Autopista Medellín–Bogotá hasta La Dorada, luego bajando al sur hacia Honda y Lérida.
            </p>
          </div>

        </div>
      </div>
    </section>

    <!-- ============================================================
         FOTO + TEXTO DE LÉRIDA — layout 50/50
    ============================================================ -->
    <section class="section-py bg-white">
      <div class="container-site px-4">
        <div class="flex flex-col lg:flex-row gap-12 items-center">

          <!-- Foto -->
          <div class="lg:w-1/2 w-full">
            <div class="overflow-hidden rounded-2xl h-72 lg:h-96 shadow-md">
              <img
                src="/img/arrozales-tolima.jpg"
                alt="Campos de arroz en Lérida, Tolima con cielo azul y nubes"
                class="w-full h-full object-cover"
              />
            </div>
          </div>

          <!-- Texto -->
          <div class="lg:w-1/2">
            <h2 class="font-display text-3xl md:text-4xl font-bold text-tierra-800 mb-6">
              Lérida — La capital del arroz colombiano
            </h2>
            <p class="text-gray-600 leading-relaxed text-base md:text-lg">
              Lérida es un municipio del norte del Tolima con poco más de veinte mil habitantes y una historia que todo colombiano debería conocer. Fue en estas tierras planas, bañadas por las aguas del Magdalena, donde se introdujeron y perfeccionaron las técnicas de cultivo de arroz que hoy abastecen al país entero. El municipio tiene ese ritmo propio de los pueblos que saben quiénes son: mercados vivos, gente directa y un calor humano que no se aprende — se hereda.
            </p>
          </div>

        </div>
      </div>
    </section>

    <!-- ============================================================
         DATOS PRÁCTICOS — 4 chips en fila
    ============================================================ -->
    <section class="py-10 bg-tierra-50">
      <div class="container-site px-4">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">

          <div class="bg-white rounded-2xl p-5 border border-tierra-100 shadow-sm text-center">
            <div class="text-3xl mb-2">🌡️</div>
            <p class="text-xs font-semibold text-tierra-700 uppercase tracking-wide mb-1">Clima</p>
            <p class="text-tierra-800 font-medium text-sm">Cálido todo el año</p>
            <p class="text-gray-500 text-xs mt-0.5">~28°C en promedio</p>
          </div>

          <div class="bg-white rounded-2xl p-5 border border-tierra-100 shadow-sm text-center">
            <div class="text-3xl mb-2">📍</div>
            <p class="text-xs font-semibold text-tierra-700 uppercase tracking-wide mb-1">Altitud</p>
            <p class="text-tierra-800 font-medium text-sm">~280 msnm</p>
            <p class="text-gray-500 text-xs mt-0.5">Norte del Tolima</p>
          </div>

          <div class="bg-white rounded-2xl p-5 border border-tierra-100 shadow-sm text-center">
            <div class="text-3xl mb-2">✈️</div>
            <p class="text-xs font-semibold text-tierra-700 uppercase tracking-wide mb-1">Aeropuerto</p>
            <p class="text-tierra-800 font-medium text-sm">Perales – Ibagué (IBO)</p>
            <p class="text-gray-500 text-xs mt-0.5">El Dorado – Bogotá (BOG)</p>
          </div>

          <div class="bg-white rounded-2xl p-5 border border-tierra-100 shadow-sm text-center">
            <div class="text-3xl mb-2">🗺️</div>
            <p class="text-xs font-semibold text-tierra-700 uppercase tracking-wide mb-1">Coordenadas</p>
            <p class="text-tierra-800 font-medium text-sm">4°51'32" N</p>
            <p class="text-gray-500 text-xs mt-0.5">74°55'16" O</p>
          </div>

        </div>
      </div>
    </section>

    <!-- ============================================================
         PLACEHOLDER DE MAPA
    ============================================================ -->
    <section class="section-py bg-white">
      <div class="container-site px-4">

        <div class="text-center max-w-xl mx-auto mb-8">
          <h2 class="font-display text-2xl md:text-3xl font-bold text-tierra-800">
            Ubicación de La Carmelita
          </h2>
        </div>

        <div class="bg-tierra-100 rounded-2xl h-64 flex flex-col items-center justify-center text-center px-6 border border-tierra-200 max-w-3xl mx-auto">
          <div class="text-5xl mb-3">📍</div>
          <p class="font-semibold text-tierra-800 text-lg mb-1">
            Hacienda La Carmelita · Lérida, Tolima
          </p>
          <p class="text-tierra-700 text-sm max-w-md">
            La ubicación exacta se comparte con la confirmación de reserva
          </p>
        </div>

        <div class="text-center mt-6">
          <NuxtLink
            to="/reservar"
            class="inline-block px-6 py-3 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-semibold text-sm transition-colors shadow"
          >
            Reservar y recibir ubicación exacta
          </NuxtLink>
        </div>

      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Cómo Llegar — Hacienda La Carmelita',
  description: 'Hacienda La Carmelita está en Lérida, Tolima. Desde Bogotá son solo 3 horas por carretera. Conoce las rutas desde Bogotá, Ibagué y Medellín para llegar al corazón del Tolima arrocero.'
})
</script>
