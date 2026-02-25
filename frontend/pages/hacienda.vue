<template>
  <div>

    <!-- ============================================================
         HERO — ~400px con foto de fondo
    ============================================================ -->
    <section
      class="relative h-[400px] flex flex-col items-center justify-center bg-cover bg-center"
      style="background-image: url('/img/hacienda-exterior-piscina.jpg')"
    >
      <div class="absolute inset-0 bg-tierra-800/60"></div>
      <div class="relative z-10 container-site px-4 text-center">
        <h1 class="font-display text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight max-w-4xl mx-auto">
          Una hacienda con alma, ochenta años de raíces
        </h1>
        <p class="mt-5 text-white/85 text-lg md:text-xl max-w-2xl mx-auto">
          Lérida, Tolima — Origen del Arroz Colombiano
        </p>
      </div>
    </section>

    <!-- ============================================================
         HISTORIA — texto + foto lateral
    ============================================================ -->
    <section class="section-py bg-white">
      <div class="container-site px-4">
        <div class="flex flex-col lg:flex-row gap-12 items-start">

          <!-- Texto (60%) -->
          <div class="lg:w-3/5">
            <h2 class="font-display text-3xl md:text-4xl font-bold text-tierra-800 mb-8">
              Una hacienda con alma, ochenta años de raíces
            </h2>
            <div class="space-y-6 text-gray-600 leading-relaxed text-base md:text-lg">
              <p>
                La Carmelita nació en los años cuarenta, cuando las primeras familias de colonos llegaron a las tierras planas del norte del Tolima con una apuesta audaz: sembrar arroz en un valle que el río Magdalena había dejado fértil durante siglos. Lérida se convirtió poco a poco en el epicentro de la revolución arrocera colombiana, y La Carmelita creció con ella — sus arrozales, su ganado Brahman y sus palmas reales son testigos de esa historia que le cambió la cara a la agricultura del país.
              </p>
              <p>
                Durante décadas, La Carmelita fue una hacienda productiva dedicada al campo, a los animales y a la tierra. Con el paso del tiempo, la familia propietaria decidió que tanta belleza no podía quedarse entre cuatro paredes: abrieron las puertas a los viajeros que buscaban algo distinto a los planes de siempre. Hoy, la misión sigue siendo preservar la cultura arrocera del Tolima y compartirla con quienes quieran entender de dónde viene la comida que los colombianos ponen en la mesa cada día.
              </p>
              <p>
                La Carmelita de hoy es una apuesta consciente por el turismo rural premium: auténtico, sostenible y profundamente colombiano. No queremos ser un resort disfrazado de hacienda. Queremos que cada huésped se vaya con tierra en los zapatos, con el olor a leña en la ropa y con la certeza de haber vivido algo real.
              </p>
            </div>
          </div>

          <!-- Foto (40%) -->
          <div class="lg:w-2/5 w-full">
            <div class="overflow-hidden rounded-2xl h-80 lg:h-full lg:min-h-[420px] shadow-md">
              <img
                src="/img/hacienda-exterior-dia.jpg"
                alt="Hacienda La Carmelita exterior desde otro ángulo"
                class="w-full h-full object-cover"
              />
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ============================================================
         INSTALACIONES — grid 2x3
    ============================================================ -->
    <section class="section-py bg-crema-50">
      <div class="container-site px-4">

        <div class="text-center max-w-2xl mx-auto mb-14">
          <h2 class="font-display text-3xl md:text-4xl font-bold text-tierra-800">
            Cada rincón tiene su historia
          </h2>
          <p class="mt-4 text-gray-600 text-lg">
            Ocho décadas de cuidado se notan en cada detalle de La Carmelita
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">

          <!-- Piscina -->
          <div class="bg-white rounded-2xl p-7 border border-tierra-100 shadow-sm hover:shadow-md transition-shadow">
            <div class="text-4xl mb-4">🏊</div>
            <h3 class="font-display text-lg font-bold text-tierra-800 mb-2">La piscina</h3>
            <p class="text-gray-600 text-sm leading-relaxed">
              Cristalina, amplia y rodeada de palmeras que han crecido con la hacienda. El lugar perfecto para las tardes de calor tolimense.
            </p>
          </div>

          <!-- Jardines -->
          <div class="bg-white rounded-2xl p-7 border border-tierra-100 shadow-sm hover:shadow-md transition-shadow">
            <div class="text-4xl mb-4">🌳</div>
            <h3 class="font-display text-lg font-bold text-tierra-800 mb-2">Los jardines centenarios</h3>
            <p class="text-gray-600 text-sm leading-relaxed">
              Árboles de más de cien años forman el marco verde de la hacienda. Los jardines son el corazón de La Carmelita.
            </p>
          </div>

          <!-- Establos -->
          <div class="bg-white rounded-2xl p-7 border border-tierra-100 shadow-sm hover:shadow-md transition-shadow">
            <div class="text-4xl mb-4">🐴</div>
            <h3 class="font-display text-lg font-bold text-tierra-800 mb-2">Los establos</h3>
            <p class="text-gray-600 text-sm leading-relaxed">
              Casa de nuestros caballos, bien cuidados y listos para llevar a los huéspedes por los cerros del Tolima.
            </p>
          </div>

          <!-- Mirador -->
          <div class="bg-white rounded-2xl p-7 border border-tierra-100 shadow-sm hover:shadow-md transition-shadow">
            <div class="text-4xl mb-4">🦒</div>
            <h3 class="font-display text-lg font-bold text-tierra-800 mb-2">El mirador de las esculturas</h3>
            <p class="text-gray-600 text-sm leading-relaxed">
              Vista de 360 grados sobre el Valle del Magdalena. Dos esculturas monumentales — una jirafa y un elefante — convierten este punto en el más fotogénico del Tolima.
            </p>
          </div>

          <!-- Rancho -->
          <div class="bg-white rounded-2xl p-7 border border-tierra-100 shadow-sm hover:shadow-md transition-shadow">
            <div class="text-4xl mb-4">🔥</div>
            <h3 class="font-display text-lg font-bold text-tierra-800 mb-2">El rancho</h3>
            <p class="text-gray-600 text-sm leading-relaxed">
              Espacio techado amplio para asados, reuniones y celebraciones. La parrilla de leña como protagonista.
            </p>
          </div>

          <!-- Habitaciones -->
          <div class="bg-white rounded-2xl p-7 border border-tierra-100 shadow-sm hover:shadow-md transition-shadow">
            <div class="text-4xl mb-4">🏡</div>
            <h3 class="font-display text-lg font-bold text-tierra-800 mb-2">Las habitaciones</h3>
            <p class="text-gray-600 text-sm leading-relaxed">
              Cómodas, con carácter colonial, capacidad para 18 huéspedes y la tranquilidad absoluta del campo.
            </p>
          </div>

        </div>
      </div>
    </section>

    <!-- ============================================================
         GALERÍA
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

        <!-- Grid 2x2 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div class="overflow-hidden rounded-2xl h-64 md:h-72 group">
            <img
              src="/img/piscina-familia.jpg"
              alt="Familia en la piscina cristalina de La Carmelita"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
          <div class="overflow-hidden rounded-2xl h-64 md:h-72 group">
            <img
              src="/img/ganado-brahman-hacienda.jpg"
              alt="Ganado Brahman junto a la piscina de la hacienda"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
          <div class="overflow-hidden rounded-2xl h-64 md:h-72 group">
            <img
              src="/img/establo-bano-caballo.jpg"
              alt="Lavando caballos en el establo con jardines al fondo"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
          <div class="overflow-hidden rounded-2xl h-64 md:h-72 group">
            <img
              src="/img/jardines-ninos-jugando.jpg"
              alt="Niños jugando fútbol bajo los árboles centenarios"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
        </div>

        <!-- Foto ancha final -->
        <div class="overflow-hidden rounded-2xl h-80 group">
          <img
            src="/img/mirador-jirafa-elefante-grupo.jpg"
            alt="Grupo en el mirador con esculturas de jirafa y elefante y el Valle del Magdalena"
            class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        </div>

      </div>
    </section>

    <!-- ============================================================
         CTA FINAL
    ============================================================ -->
    <section class="section-py bg-tierra-800">
      <div class="container-site px-4 text-center">
        <h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-5">
          ¿Listo para conocerla?
        </h2>
        <p class="text-tierra-200 text-lg max-w-xl mx-auto mb-8">
          Disponibilidad limitada — la hacienda recibe solo un grupo a la vez.
        </p>
        <NuxtLink
          to="/reservar"
          class="inline-block px-10 py-4 rounded-xl bg-dorado-500 hover:bg-dorado-600 text-white font-bold text-lg shadow-xl transition-colors"
        >
          Reservar mi estadía
        </NuxtLink>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'La Hacienda — Hacienda La Carmelita',
  description: 'Conoce la historia de Hacienda La Carmelita: 80 años de raíces en Lérida, Tolima. Piscina, jardines centenarios, establos, mirador de esculturas y gastronomía a la leña en el corazón del Tolima.'
})
</script>
