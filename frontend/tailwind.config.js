/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50: '#FFFDF9',
          100: '#FFF9F2',
          200: '#FDF2E7',
        },
        rose: {
          50: '#FDF2F8',
          100: '#FCE7F0',
          200: '#FBCFE8',
          300: '#F472B6',
          400: '#E879F9',
          500: '#DB2777',
          600: '#BE185D',
          700: '#9D174D',
        },
        plum: {
          800: '#2D1B2D',
          900: '#1E1B1E',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Outfit', 'Inter', 'sans-serif'],
        display: ['Outfit', 'Plus Jakarta Sans', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 10px 30px -10px rgba(219, 39, 119, 0.1)',
        'y2k': '4px 4px 0px 0px rgba(219, 39, 119, 0.2)',
        'glass': '0 8px 32px 0 rgba(244, 114, 182, 0.15)',
      }
    },
  },
  plugins: [],
}
