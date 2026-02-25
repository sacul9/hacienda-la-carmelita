import type { Config } from 'tailwindcss'

export default {
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue',
    './error.vue',
  ],
  theme: {
    extend: {
      colors: {
        // Paleta Hacienda La Carmelita
        tierra: {
          50:  '#f4f7f0',
          100: '#e6eddc',
          200: '#ccdcbb',
          300: '#a9c390',
          400: '#82a663',
          500: '#618945',
          600: '#4a6d33',
          700: '#3a562a',
          800: '#2D5016', // PRIMARY — verde tierra
          900: '#243d14',
          950: '#122009',
        },
        dorado: {
          50:  '#fdfbeb',
          100: '#faf3c7',
          200: '#f6e88f',
          300: '#f0d44e',
          400: '#e8bf26',
          500: '#C9A227', // PRIMARY — dorado
          600: '#a87a19',
          700: '#865917',
          800: '#704719',
          900: '#5f3b1b',
          950: '#361e0a',
        },
        crema: {
          50:  '#FAFAF7', // fondo principal
          100: '#f5f5ef',
          200: '#eaeade',
          300: '#d8d8c6',
          400: '#c0c0a8',
          500: '#a5a588',
          600: '#8a8a6e',
          700: '#716f58',
          800: '#5d5c49',
          900: '#4e4d3e',
        },
      },
      fontFamily: {
        display: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'hero': ['clamp(2.5rem, 5vw, 4.5rem)', { lineHeight: '1.1', fontWeight: '700' }],
        'heading': ['clamp(1.75rem, 3vw, 2.5rem)', { lineHeight: '1.2', fontWeight: '600' }],
      },
      maxWidth: {
        'site': '1280px',
      },
      backgroundImage: {
        'gradient-tierra': 'linear-gradient(135deg, #2D5016 0%, #4a6d33 100%)',
        'gradient-dorado': 'linear-gradient(135deg, #C9A227 0%, #e8bf26 100%)',
      },
    },
  },
  plugins: [],
} satisfies Config
