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
      },
    ],
  },
}