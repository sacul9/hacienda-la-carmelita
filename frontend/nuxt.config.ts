export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n',
    '@pinia/nuxt',
    '@vee-validate/nuxt',
    '@nuxt/image',
    '@vite-pwa/nuxt',
    '@vueuse/nuxt',
    '@nuxt/eslint',
    '@pinia-plugin-persistedstate/nuxt',
  ],

  // Configuración i18n
  i18n: {
    locales: [
      { code: 'es', language: 'es-CO', name: 'Español', file: 'es.json' },
      { code: 'en', language: 'en-US', name: 'English', file: 'en.json' },
    ],
    defaultLocale: 'es',
    lazy: true,
    langDir: 'locales/',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root',
    },
  },

  // PWA
  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'Hacienda La Carmelita',
      short_name: 'La Carmelita',
      description: 'Finca turística premium en Lérida, Tolima, Colombia',
      theme_color: '#2D5016',
      background_color: '#ffffff',
      display: 'standalone',
      orientation: 'portrait',
      icons: [
        { src: '/icons/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
        { src: '/icons/pwa-512x512.png', sizes: '512x512', type: 'image/png' },
        { src: '/icons/pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico}'],
    },
  },

  // Optimización de imágenes
  image: {
    quality: 80,
    format: ['webp'],
    screens: {
      xs: 320,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
      xxl: 1536,
    },
  },

  // Variables de entorno del frontend
  runtimeConfig: {
    // Server-only
    apiSecret: '',
    // Public (client)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      wompiPublicKey: process.env.NUXT_PUBLIC_WOMPI_KEY || '',
      stripePublicKey: process.env.NUXT_PUBLIC_STRIPE_KEY || '',
      googleMapsKey: process.env.NUXT_PUBLIC_GMAPS_KEY || '',
      posthogKey: process.env.NUXT_PUBLIC_POSTHOG_KEY || '',
    },
  },

  // SSR habilitado para SEO
  ssr: true,

  // Tailwind
  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: 'tailwind.config.ts',
  },

  // App head defaults
  app: {
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      link: [
        {
          rel: 'preconnect',
          href: 'https://fonts.googleapis.com',
        },
        {
          rel: 'preconnect',
          href: 'https://fonts.gstatic.com',
          crossorigin: '',
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap',
        },
      ],
    },
  },

  // Registrar componentes sin prefijo de carpeta (BaseCard, BaseButton, etc.)
  components: {
    dirs: [{ path: '~/components', pathPrefix: false }],
  },

  compatibilityDate: '2024-11-01',
})
