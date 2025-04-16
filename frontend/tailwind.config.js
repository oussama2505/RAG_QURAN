/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('daisyui')
  ],
  daisyui: {
    themes: [
      {
        light: {
          ...require('daisyui/src/theming/themes')['light'],
          primary: '#2C5282',
          secondary: '#38A169',
          accent: '#E8DCC4',
          neutral: '#2D3748',
          'base-100': '#FFFFFF',
        },
        dark: {
          ...require('daisyui/src/theming/themes')['dark'],
          primary: '#90CDF4',     // Azul más claro para mejor contraste en oscuro
          secondary: '#9AE6B4',   // Verde más claro 
          accent: '#F0E6D2',      // Acento más claro para mejor contraste
          neutral: '#E2E8F0',     // Texto claro para mejor legibilidad
          'base-100': '#121520',  // Fondo principal más oscuro y con tono azulado
          'base-200': '#1E212D',  // Fondo secundario con tinte azulado
          'base-300': '#2D3348',  // Fondo terciario con tinte azulado
          'base-content': '#E2E8F0', // Color de texto principal
          'neutral-content': '#F7FAFC', // Color de texto para elementos neutrales
        }
      },
    ],
  },
}