<template>
  <header class="bg-white/95 backdrop-blur-sm border-b border-gray-100 sticky top-0 z-40">
    <div class="container-site">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <NuxtLink :to="localePath('/')" class="flex items-center gap-2">
          <span class="font-display text-xl font-bold text-tierra-800">
            Hacienda La Carmelita
          </span>
        </NuxtLink>

        <!-- Nav desktop -->
        <nav class="hidden md:flex items-center gap-6">
          <NuxtLink :to="localePath('/')" class="text-sm font-medium text-gray-600 hover:text-tierra-800 transition-colors">
            {{ $t('nav.home') }}
          </NuxtLink>
          <NuxtLink :to="localePath('/hacienda')" class="text-sm font-medium text-gray-600 hover:text-tierra-800 transition-colors">
            {{ $t('nav.hacienda') }}
          </NuxtLink>
          <NuxtLink :to="localePath('/experiencias')" class="text-sm font-medium text-gray-600 hover:text-tierra-800 transition-colors">
            {{ $t('nav.experiences') }}
          </NuxtLink>
          <NuxtLink :to="localePath('/blog')" class="text-sm font-medium text-gray-600 hover:text-tierra-800 transition-colors">
            Blog
          </NuxtLink>
          <NuxtLink :to="localePath('/ubicacion')" class="text-sm font-medium text-gray-600 hover:text-tierra-800 transition-colors">
            {{ $t('nav.location') }}
          </NuxtLink>
        </nav>

        <!-- Actions -->
        <div class="flex items-center gap-3">
          <!-- Language switcher -->
          <button
            class="hidden md:block text-sm font-medium text-gray-500 hover:text-tierra-800 transition-colors"
            @click="switchLocale"
          >
            {{ currentLocale === 'es' ? 'EN' : 'ES' }}
          </button>
          <!-- CTA desktop -->
          <BaseButton :to="localePath('/reservar')" size="sm" class="hidden md:inline-flex">
            {{ $t('nav.book') }}
          </BaseButton>
          <!-- Hamburger móvil -->
          <button
            class="md:hidden p-2 rounded-lg text-gray-600 hover:text-tierra-800 hover:bg-gray-100 transition-colors"
            :aria-label="menuAbierto ? 'Cerrar menú' : 'Abrir menú'"
            @click="menuAbierto = !menuAbierto"
          >
            <svg v-if="!menuAbierto" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Menú móvil -->
    <div v-if="menuAbierto" class="md:hidden border-t border-gray-100 bg-white/95 backdrop-blur-sm">
      <nav class="container-site py-4 flex flex-col gap-1">
        <NuxtLink
          :to="localePath('/')"
          class="px-4 py-2.5 rounded-lg text-sm font-medium text-gray-700 hover:bg-tierra-50 hover:text-tierra-800 transition-colors"
          @click="menuAbierto = false"
        >
          {{ $t('nav.home') }}
        </NuxtLink>
        <NuxtLink
          :to="localePath('/hacienda')"
          class="px-4 py-2.5 rounded-lg text-sm font-medium text-gray-700 hover:bg-tierra-50 hover:text-tierra-800 transition-colors"
          @click="menuAbierto = false"
        >
          {{ $t('nav.hacienda') }}
        </NuxtLink>
        <NuxtLink
          :to="localePath('/experiencias')"
          class="px-4 py-2.5 rounded-lg text-sm font-medium text-gray-700 hover:bg-tierra-50 hover:text-tierra-800 transition-colors"
          @click="menuAbierto = false"
        >
          {{ $t('nav.experiences') }}
        </NuxtLink>
        <NuxtLink
          :to="localePath('/blog')"
          class="px-4 py-2.5 rounded-lg text-sm font-medium text-gray-700 hover:bg-tierra-50 hover:text-tierra-800 transition-colors"
          @click="menuAbierto = false"
        >
          Blog
        </NuxtLink>
        <NuxtLink
          :to="localePath('/ubicacion')"
          class="px-4 py-2.5 rounded-lg text-sm font-medium text-gray-700 hover:bg-tierra-50 hover:text-tierra-800 transition-colors"
          @click="menuAbierto = false"
        >
          {{ $t('nav.location') }}
        </NuxtLink>
        <div class="mt-2 pt-3 border-t border-gray-100 flex items-center justify-between px-4">
          <button
            class="text-sm font-medium text-gray-500 hover:text-tierra-800 transition-colors"
            @click="switchLocale"
          >
            {{ currentLocale === 'es' ? 'EN' : 'ES' }}
          </button>
          <BaseButton :to="localePath('/reservar')" size="sm" @click="menuAbierto = false">
            {{ $t('nav.book') }}
          </BaseButton>
        </div>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
const { locale, locales, setLocale } = useI18n()
const localePath = useLocalePath()

const currentLocale = computed(() => locale.value)
const menuAbierto = ref(false)

const switchLocale = () => {
  const next = currentLocale.value === 'es' ? 'en' : 'es'
  setLocale(next)
}

// Cerrar menú al cambiar de ruta
const route = useRoute()
watch(() => route.path, () => { menuAbierto.value = false })
</script>
