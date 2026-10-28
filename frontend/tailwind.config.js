/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Aktywuje tryb ciemny bazujący na klasie 'dark'
  theme: {
    extend: {
      colors: {
        custom: {
          dark: '#060606',    // Główne tło (color1)
          card: '#222327',    // Tło kart / navbaru (color2)
          border: '#52545d',  // Obramowania (color3)
          muted: '#8e9097',   // Szary tekst (color4)
          light: '#cccedc',   // Jasny tekst / nagłówki (color5)
        }
      }
    },
  },
  plugins: [],
}