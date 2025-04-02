/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: '#646cff',
        secondary: '#535bf2',
        text: { DEFAULT: 'rgba(255, 255, 255, 0.87)', dark: '#213547' },
        background: { DEFAULT: '#242424', light: '#ffffff' }
      }
    }
  },
  plugins: []
};