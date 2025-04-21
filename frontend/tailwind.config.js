// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}", // Эта строка важна
  ],
  theme: {
    extend: {
      // Здесь можно добавить свои цвета, шрифты и т.д. для самурайской темы
      colors: {
        'samurai-red': '#B42B3F',
        'samurai-dark': '#1a1a1a',
        'samurai-gold': '#D4AF37',
        'terminal-green': '#4AF626',
      },
      fontFamily: {
        // Можно подключить кастомный шрифт, если найдете подходящий
        // sans: ['Inter', 'sans-serif'], // Пример
      }
    },
  },
  plugins: [],
}