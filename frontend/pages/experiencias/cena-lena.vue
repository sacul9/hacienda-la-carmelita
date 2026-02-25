<template>
  <div>

    <!-- HERO -->
    <section
      class="relative h-[420px] flex flex-col items-center justify-center bg-cover bg-center"
      style="background-image: url('/img/gastronomia-bbq-parrilla.jpg')"
    >
      <div class="absolute inset-0 bg-tierra-800/65"></div>
      <div class="relative z-10 container-site px-4 text-center">
        <NuxtLink to="/experiencias" class="inline-flex items-center gap-2 text-white/70 hover:text-white text-sm mb-6 transition-colors">
          ← Todas las experiencias
        </NuxtLink>
        <span class="block mb-4 px-4 py-1.5 rounded-full border border-dorado-400/70 bg-black/30 text-dorado-400 text-sm font-medium tracking-wide w-fit mx-auto">
          🍖 Gastronomía
        </span>
        <h1 class="font-display text-4xl md:text-5xl font-bold text-white leading-tight max-w-3xl mx-auto">
          Cena a la Leña — BBQ Bajo las Estrellas del Tolima
        </h1>
        <p class="mt-4 text-white/85 text-lg max-w-2xl mx-auto leading-relaxed">
          Cortes premium cocinados a fuego de leña en los jardines centenarios de la hacienda.
        </p>
      </div>
    </section>

    <!-- CONTENIDO PRINCIPAL -->
    <section class="section-py bg-crema-50">
      <div class="container-site px-4">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">

          <div class="lg:col-span-2 space-y-8">

            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">La experiencia</h2>
              <div class="text-gray-600 leading-relaxed space-y-4">
                <p>En La Carmelita no se hace glamping de Pinterest. Se hace fuego de verdad. Con leña cortada en la finca, una parrilla de hierro fundido y cortes de res criada en las mismas llanuras del Tolima.</p>
                <p>La cena se sirve en los jardines de la hacienda, bajo un cielo sin contaminación lumínica donde la Vía Láctea es visible a simple vista la mayor parte del año.</p>
                <p>El menú cambia según la temporada, pero siempre hay lomo de res, chorizos artesanales de la región y papas criollas con hogao. La bebida de bienvenida es limonada de panela con menta del jardín.</p>
              </div>
            </div>

            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">El menú de la noche</h2>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div v-for="plato in menu" :key="plato.nombre" class="bg-white rounded-xl border border-tierra-100 p-4">
                  <p class="font-semibold text-tierra-800 mb-1">{{ plato.nombre }}</p>
                  <p class="text-sm text-gray-500">{{ plato.descripcion }}</p>
                </div>
              </div>
              <p class="text-xs text-gray-400 mt-3">* El menú puede variar según disponibilidad de temporada.</p>
            </div>

            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">Qué incluye</h2>
              <ul class="space-y-3">
                <li v-for="item in incluye" :key="item" class="flex items-start gap-3 text-gray-600">
                  <span class="text-dorado-500 font-bold text-lg leading-tight">✓</span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>

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

          <!-- Sidebar -->
          <div class="lg:col-span-1">
            <div class="sticky top-6 bg-white rounded-2xl border border-tierra-100 shadow-sm p-6 space-y-5">
              <h3 class="font-display text-xl font-bold text-tierra-800">Reservar</h3>
              <div class="space-y-3">
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">⏱</span><span>Aproximadamente 2 horas</span></div>
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">👥</span><span>Hasta 18 personas</span></div>
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">🌙</span><span>Solo en la noche</span></div>
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">🗓️</span><span>Con reserva previa (48h)</span></div>
              </div>
              <div class="border-t border-tierra-100 pt-4">
                <p class="text-sm text-gray-500 mb-1">Precio por persona</p>
                <p class="font-display text-3xl font-bold text-tierra-800">$120.000 <span class="text-base font-normal text-gray-500">COP</span></p>
                <p class="text-xs text-gray-400 mt-1">Disponible como add-on en cualquier paquete</p>
              </div>
              <NuxtLink to="/reservar" class="block text-center w-full px-6 py-4 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-bold text-base transition-colors">
                Reservar con cena
              </NuxtLink>
              <a href="https://wa.me/573001234567?text=Hola%2C+quiero+información+sobre+la+cena+a+la+leña" target="_blank" class="block text-center w-full px-6 py-3 rounded-xl border border-tierra-200 hover:bg-tierra-50 text-tierra-800 font-semibold text-sm transition-colors">
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
  title: 'Cena a la Leña — Hacienda La Carmelita, Lérida, Tolima',
  description: 'BBQ bajo las estrellas del Tolima con cortes premium a fuego de leña en los jardines centenarios de La Carmelita. Reserva tu noche especial.'
})

const menu = [
  { nombre: 'Lomo de res a la leña', descripcion: 'Marinado 12 horas con hierbas del jardín' },
  { nombre: 'Chorizos artesanales del Tolima', descripcion: 'Elaborados por proveedores locales de Lérida' },
  { nombre: 'Papas criollas con hogao', descripcion: 'Receta tradicional tolimense, al carbón' },
  { nombre: 'Ensalada de temporada', descripcion: 'Vegetales frescos de la despensa de la hacienda' },
  { nombre: 'Limonada de panela con menta', descripcion: 'Panela de Armero, menta del jardín' },
  { nombre: 'Postre de la finca', descripcion: 'Piña, papayuela o arequipe casero según temporada' },
]

const incluye = [
  'Menú completo por persona',
  'Bebida de bienvenida y agua durante la cena',
  'Servicio de mesa en los jardines de la hacienda',
  'Montaje especial con iluminación bajo las estrellas',
]

const faqs = [
  { q: '¿Se puede adaptar para vegetarianos?', a: 'Sí. Con 48 horas de anticipación preparamos alternativas sin carne o sin gluten. Indícanoslo al reservar.' },
  { q: '¿Está incluida en los paquetes de estadía?', a: 'Es un add-on que se puede agregar a cualquier paquete al momento de reservar.' },
  { q: '¿Qué pasa si llueve?', a: 'Tenemos zona cubierta para lluvia leve. Si hace frío, proveemos cobijas y encendemos el fogón central.' },
]
</script>
