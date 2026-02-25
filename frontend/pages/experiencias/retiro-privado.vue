<template>
  <div>

    <!-- HERO -->
    <section
      class="relative h-[480px] flex flex-col items-center justify-center bg-cover bg-center"
      style="background-image: url('/img/hacienda-exterior-piscina.jpg')"
    >
      <div class="absolute inset-0 bg-tierra-800/60"></div>
      <div class="relative z-10 container-site px-4 text-center">
        <NuxtLink to="/experiencias" class="inline-flex items-center gap-2 text-white/70 hover:text-white text-sm mb-6 transition-colors">
          ← Todas las experiencias
        </NuxtLink>
        <span class="block mb-4 px-4 py-1.5 rounded-full border border-dorado-400/70 bg-black/30 text-dorado-400 text-sm font-medium tracking-wide w-fit mx-auto">
          ❤️ Romance · Exclusividad
        </span>
        <h1 class="font-display text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight max-w-3xl mx-auto">
          Retiro Privado — La Carmelita Solo para Ustedes Dos
        </h1>
        <p class="mt-4 text-white/85 text-lg max-w-2xl mx-auto leading-relaxed">
          La hacienda completa — 100 hectáreas, piscina, mirador y jardines — reservada exclusivamente para una pareja.
        </p>
      </div>
    </section>

    <!-- PROPUESTA DE VALOR diferencial -->
    <section class="py-12 bg-dorado-50 border-y border-dorado-200">
      <div class="container-site px-4 text-center">
        <p class="font-display text-xl md:text-2xl text-tierra-800 font-semibold max-w-2xl mx-auto">
          "No compartirán La Carmelita con nadie. Ni la piscina, ni el mirador, ni los jardines. Toda la finca es de ustedes."
        </p>
        <p class="mt-3 text-gray-500 text-sm">Disponible de viernes a domingo</p>
      </div>
    </section>

    <!-- CONTENIDO PRINCIPAL -->
    <section class="section-py bg-crema-50">
      <div class="container-site px-4">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">

          <div class="lg:col-span-2 space-y-8">

            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">Por qué funciona</h2>
              <div class="text-gray-600 leading-relaxed space-y-4">
                <p>La mayoría de los planes románticos en Colombia son predecibles: hotel boutique en la ciudad, spa corporativo, cena con menú fijo. El Retiro Privado de La Carmelita es lo opuesto.</p>
                <p>Son dos noches en una hacienda centenaria del Tolima donde tú eres el único huésped. Sin recepcionistas, sin otros huéspedes, sin ruido. Solo ustedes, 100 hectáreas de campo, una piscina con vista al valle y el equipo de la finca disponible para cualquier cosa que necesiten.</p>
                <p>La primera noche hay cena a la leña en los jardines. La segunda, picnic en el mirador si el clima acompaña. El desayuno del segundo día lo sirven en la hacienda con productos de la finca.</p>
              </div>
            </div>

            <!-- Galería -->
            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">La hacienda</h2>
              <div class="grid grid-cols-2 gap-3">
                <img src="/img/hacienda-exterior-piscina.jpg" alt="Piscina de la hacienda" class="rounded-xl h-44 w-full object-cover" />
                <img src="/img/hacienda-exterior-dia.jpg" alt="Fachada colonial de la hacienda" class="rounded-xl h-44 w-full object-cover" />
                <img src="/img/mirador-jirafa-elefante-grupo.jpg" alt="Mirador con esculturas" class="rounded-xl h-44 w-full object-cover" />
                <img src="/img/jardines-ninos-prado.jpg" alt="Jardines de la hacienda" class="rounded-xl h-44 w-full object-cover" />
              </div>
            </div>

            <!-- Itinerario sugerido -->
            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">Itinerario sugerido (2 noches)</h2>
              <div class="space-y-4">
                <div v-for="item in itinerario" :key="item.momento" class="flex gap-4">
                  <div class="flex-shrink-0 w-24 text-right">
                    <span class="text-xs font-semibold text-dorado-600 uppercase tracking-wide">{{ item.momento }}</span>
                  </div>
                  <div class="flex-1 border-l-2 border-tierra-100 pl-4 pb-4">
                    <p class="font-semibold text-tierra-800 text-sm">{{ item.actividad }}</p>
                    <p class="text-sm text-gray-500 mt-0.5">{{ item.detalle }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Incluye -->
            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">Qué incluye</h2>
              <ul class="space-y-3">
                <li v-for="item in incluye" :key="item" class="flex items-start gap-3 text-gray-600">
                  <span class="text-dorado-500 font-bold text-lg leading-tight">✓</span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>

          </div>

          <!-- Sidebar -->
          <div class="lg:col-span-1">
            <div class="sticky top-6 bg-white rounded-2xl border border-tierra-100 shadow-sm p-6 space-y-5">
              <h3 class="font-display text-xl font-bold text-tierra-800">Consultar disponibilidad</h3>
              <div class="space-y-3">
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">🗓️</span><span>Mínimo 2 noches</span></div>
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">👫</span><span>Solo para 2 personas</span></div>
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">🏡</span><span>Hacienda completa exclusiva</span></div>
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">📅</span><span>Viernes a domingo preferiblemente</span></div>
              </div>
              <div class="border-t border-tierra-100 pt-4">
                <p class="text-sm text-gray-500 mb-1">Precio desde</p>
                <p class="font-display text-3xl font-bold text-tierra-800">$1.200.000 <span class="text-base font-normal text-gray-500">COP / noche</span></p>
                <p class="text-xs text-gray-400 mt-1">Incluye cena a la leña, desayuno y mirador</p>
              </div>
              <NuxtLink to="/reservar" class="block text-center w-full px-6 py-4 rounded-xl bg-dorado-500 hover:bg-dorado-600 text-white font-bold text-base transition-colors">
                Consultar disponibilidad
              </NuxtLink>
              <a href="https://wa.me/573001234567?text=Hola%2C+quiero+información+sobre+el+retiro+privado+para+parejas" target="_blank" class="block text-center w-full px-6 py-3 rounded-xl border border-tierra-200 hover:bg-tierra-50 text-tierra-800 font-semibold text-sm transition-colors">
                💬 Hablar por WhatsApp
              </a>
              <p class="text-xs text-gray-400 text-center">
                Cupos muy limitados. Máximo 2 retiros privados por mes.
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Retiro Privado para Parejas — Hacienda La Carmelita, Tolima',
  description: 'La hacienda completa solo para ustedes dos. 100 hectáreas, piscina, mirador y cena a la leña. El plan romántico más exclusivo del Tolima. Lérida, Colombia.'
})

const itinerario = [
  { momento: 'Viernes 3pm', actividad: 'Llegada y bienvenida', detalle: 'Recepción con limonada de panela. Recorrido privado por la hacienda.' },
  { momento: 'Viernes 7pm', actividad: 'Cena a la leña', detalle: 'Menú completo en los jardines con iluminación especial.' },
  { momento: 'Sábado 8am', actividad: 'Desayuno en la hacienda', detalle: 'Huevos de la finca, arepas de chócolo, mermelada de guayaba casera.' },
  { momento: 'Sábado 10am', actividad: 'Cabalgata al mirador', detalle: 'Ruta privada hasta el mirador de las esculturas. Vista 360° del Valle del Magdalena.' },
  { momento: 'Sábado tarde', actividad: 'Tarde libre', detalle: 'Piscina, hamacas y silencio. Sin itinerarios.' },
  { momento: 'Sábado 6pm', actividad: 'Picnic en el mirador', detalle: 'Si el clima acompaña: quesos, vino y el atardecer del Tolima.' },
  { momento: 'Domingo 9am', actividad: 'Desayuno y partida', detalle: 'Check-out flexible hasta las 2pm.' },
]

const incluye = [
  '2 noches en la hacienda exclusiva para la pareja',
  'Decoración romántica en la habitación principal',
  'Cena completa a la leña la primera noche',
  'Desayunos ambos días con productos de la finca',
  'Cabalgata privada al mirador',
  'Picnic en el mirador (sujeto a clima)',
  'Piscina privada durante toda la estadía',
  'Acceso libre al mirador de esculturas las 24h',
]
</script>
