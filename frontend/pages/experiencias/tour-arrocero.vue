<template>
  <div>

    <!-- HERO -->
    <section
      class="relative h-[420px] flex flex-col items-center justify-center bg-cover bg-center"
      style="background-image: url('/img/arrozales-tolima.jpg')"
    >
      <div class="absolute inset-0 bg-tierra-800/65"></div>
      <div class="relative z-10 container-site px-4 text-center">
        <NuxtLink to="/experiencias" class="inline-flex items-center gap-2 text-white/70 hover:text-white text-sm mb-6 transition-colors">
          ← Todas las experiencias
        </NuxtLink>
        <span class="block mb-4 px-4 py-1.5 rounded-full border border-dorado-400/70 bg-black/30 text-dorado-400 text-sm font-medium tracking-wide w-fit mx-auto">
          🌾 Cultura
        </span>
        <h1 class="font-display text-4xl md:text-5xl font-bold text-white leading-tight max-w-3xl mx-auto">
          Tour del Arroz — En el Origen de una Tradición
        </h1>
        <p class="mt-4 text-white/85 text-lg max-w-2xl mx-auto leading-relaxed">
          Camina entre los arrozales de Lérida y aprende cómo nació la industria que convirtió al Tolima en la despensa arrocera de Colombia.
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
                <p>Lérida, Tolima, es uno de los municipios con más hectáreas de arroz en Colombia. La Carmelita tiene 100 de ellas. Este tour es un recorrido por esas hectáreas con la persona que las ha sembrado durante toda su vida.</p>
                <p>En el tour conocerás el ciclo completo del arroz: la preparación del suelo, la siembra, el control del agua en los tablones, la cosecha mecánica y el proceso de pilada que convierte el arroz paddy en el grano blanco que llega a tu mesa.</p>
                <p>Al final, se sirve un almuerzo típico tolimense con arroz de la finca, sancocho de gallina criolla y lechona en miniatura preparada por el equipo de la hacienda.</p>
              </div>
            </div>

            <!-- Fases del tour -->
            <div>
              <h2 class="font-display text-2xl font-bold text-tierra-800 mb-4">Las 4 fases del recorrido</h2>
              <div class="space-y-4">
                <div v-for="(fase, i) in fases" :key="fase.titulo" class="flex gap-4 bg-white rounded-xl border border-tierra-100 p-5">
                  <div class="flex-shrink-0 w-10 h-10 rounded-full bg-tierra-800 text-white flex items-center justify-center font-bold text-sm">
                    {{ i + 1 }}
                  </div>
                  <div>
                    <p class="font-semibold text-tierra-800 mb-1">{{ fase.titulo }}</p>
                    <p class="text-sm text-gray-600 leading-relaxed">{{ fase.descripcion }}</p>
                  </div>
                </div>
              </div>
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
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">⏱</span><span>2 horas (+ almuerzo opcional)</span></div>
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">👥</span><span>Grupos hasta 18 personas</span></div>
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">☀️</span><span>Solo en la mañana (7am–12m)</span></div>
                <div class="flex items-center gap-3 text-sm text-gray-600"><span class="text-dorado-500">👟</span><span>Botas de caucho recomendadas</span></div>
              </div>
              <div class="border-t border-tierra-100 pt-4">
                <p class="text-sm text-gray-500 mb-1">Precio por persona</p>
                <p class="font-display text-3xl font-bold text-tierra-800">$45.000 <span class="text-base font-normal text-gray-500">COP</span></p>
                <p class="text-xs text-gray-400 mt-1">Almuerzo típico: $35.000 adicionales</p>
              </div>
              <NuxtLink to="/reservar" class="block text-center w-full px-6 py-4 rounded-xl bg-tierra-800 hover:bg-tierra-900 text-white font-bold text-base transition-colors">
                Reservar estadía + tour
              </NuxtLink>
              <a href="https://wa.me/573001234567?text=Hola%2C+quiero+información+sobre+el+tour+del+arroz" target="_blank" class="block text-center w-full px-6 py-3 rounded-xl border border-tierra-200 hover:bg-tierra-50 text-tierra-800 font-semibold text-sm transition-colors">
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
  title: 'Tour del Arroz — Hacienda La Carmelita, Lérida, Tolima',
  description: 'Recorre los 100 hectáreas de arrozales de La Carmelita y aprende el proceso completo del arroz tolimense. Incluye almuerzo típico. Lérida, Tolima, Colombia.'
})

const fases = [
  {
    titulo: 'El tablón: preparación y siembra',
    descripcion: 'Comienza en los tablones de barro donde el arroz empieza su vida. El agrónomo de la finca explica cómo se nivela el suelo para controlar el agua y cuándo se siembra.',
  },
  {
    titulo: 'El cultivo: 90 días bajo el agua',
    descripcion: 'Caminas entre las plantas en plena floración. Aprenderás a distinguir el arroz de primera y segunda calidad, y por qué el microclima de Lérida produce granos más grandes.',
  },
  {
    titulo: 'La cosecha mecánica',
    descripcion: 'Si la temporada coincide, verás la cosechadora en acción. Si no, hay un video del proceso con comentario del operador que trabaja en la finca hace 15 años.',
  },
  {
    titulo: 'La piladora: del paddy al blanco',
    descripcion: 'En la planta de pilada conocerás la maquinaria que descascara, pule y clasifica el arroz. Podrás llevarte una bolsa de arroz recién pilado de La Carmelita.',
  },
]

const incluye = [
  'Guía agrónomo de la finca',
  'Recorrido completo por tablones y planta de pilada',
  'Botas de caucho prestadas para el recorrido en los tablones',
  'Bolsa de arroz de La Carmelita para llevar a casa',
  'Agua durante todo el recorrido',
]

const faqs = [
  { q: '¿El tour es adecuado para niños?', a: 'Completamente. A los niños les encanta caminar entre el barro de los tablones. Recomendamos ropa que no les importe ensuciar.' },
  { q: '¿En qué temporada hay cosecha?', a: 'En Lérida hay dos cosechas al año: marzo–abril y septiembre–octubre. Fuera de temporada, el tour se hace con el cultivo en crecimiento.' },
  { q: '¿Se puede hacer sin estadía previa?', a: 'El tour es para huéspedes de la hacienda. Si quieres visitarlo sin estadía, contáctanos por WhatsApp.' },
]
</script>
