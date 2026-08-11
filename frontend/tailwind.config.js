/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#FFF5F0',
          100: '#FFEFEA',
          200: '#FFD8CC',
          500: '#FF6B00',
          600: '#FF5500',
          700: '#E64D00',
        },
        orange: {
          50: '#FFF5F0',
          100: '#FFEFEA',
          200: '#FFD8CC',
          500: '#FF6B00',
          600: '#FF5500',
          700: '#E64D00',
        },
      },
      animation: {
        'fade-up': 'fadeUp 0.3s ease-out',
        'pulse-subtle': 'pulseSubtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'wave-bar': 'waveBar 1.2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        waveBar: {
          '0%': { height: '4px' },
          '100%': { height: '16px' },
        },
      },
    },
  },
  plugins: [],
}
