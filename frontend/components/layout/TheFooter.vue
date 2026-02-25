<template>
  <footer class="bg-tierra-900 text-white">
    <div class="container-site py-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Brand -->
        <div>
          <h3 class="font-display text-xl font-semibold mb-3">Hacienda La Carmelita</h3>
          <p class="text-tierra-200 text-sm leading-relaxed">
            Lérida, Tolima — Colombia<br>
            Origen del Arroz Colombiano
          </p>
          <div class="flex gap-4 mt-4">
            <a href="#" class="text-tierra-300 hover:text-white transition-colors text-sm">Instagram</a>
            <a href="#" class="text-tierra-300 hover:text-white transition-colors text-sm">TikTok</a>
            <a href="#" class="text-tierra-300 hover:text-white transition-colors text-sm">WhatsApp</a>
          </div>
        </div>
        <!-- Links -->
        <div>
          <h4 class="font-semibold text-sm uppercase tracking-wider text-tierra-300 mb-3">Explora</h4>
          <ul class="space-y-2">
            <li><NuxtLink :to="localePath('/')" class="text-tierra-200 hover:text-white text-sm transition-colors">Inicio</NuxtLink></li>
            <li><NuxtLink :to="localePath('/hacienda')" class="text-tierra-200 hover:text-white text-sm transition-colors">La Hacienda</NuxtLink></li>
            <li><NuxtLink :to="localePath('/experiencias')" class="text-tierra-200 hover:text-white text-sm transition-colors">Experiencias</NuxtLink></li>
            <li><NuxtLink :to="localePath('/blog')" class="text-tierra-200 hover:text-white text-sm transition-colors">Blog</NuxtLink></li>
            <li><NuxtLink :to="localePath('/ubicacion')" class="text-tierra-200 hover:text-white text-sm transition-colors">Cómo llegar</NuxtLink></li>
          </ul>
        </div>
        <!-- Contact -->
        <div>
          <h4 class="font-semibold text-sm uppercase tracking-wider text-tierra-300 mb-3">Contacto</h4>
          <ul class="space-y-2 text-sm text-tierra-200">
            <li>reservas@haciendalacarmelita.com</li>
            <li>+57 (xxx) xxx-xxxx</li>
            <li>Lérida, Tolima, Colombia</li>
          </ul>
        </div>
      </div>
      <div class="border-t border-tierra-800 mt-8 pt-6 text-center text-tierra-400 text-xs">
        © {{ new Date().getFullYear() }} Hacienda La Carmelita. Todos los derechos reservados.
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
</script>
