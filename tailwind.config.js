/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          950: '#081A13',
          900: '#0C261D',
          850: '#113327',
          800: '#164233',
          700: '#1E5845',
          600: '#27755C',
          500: '#339777',
        },
        ivory: {
          50: '#FDFBF7',
          100: '#F9F5EC',
          200: '#F1E9D7',
          300: '#E4D5B8',
          400: '#D5BE95',
          500: '#C2A36B',
        },
        parchment: {
          bg: '#FAF7F0',
          card: '#F4EFE3',
          border: '#E3D8C3',
        },
        gold: {
          400: '#E7BD6E',
          500: '#D4A359',
          600: '#B6843A',
        }
      },
      fontFamily: {
        serif: ['Outfit', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
        kannada: ['"Noto Sans Kannada"', 'sans-serif'],
      },
      boxShadow: {
        'glow-emerald': '0 0 30px -5px rgba(39, 117, 92, 0.4)',
        'glow-gold': '0 0 25px -5px rgba(212, 163, 89, 0.35)',
        'premium': '0 20px 40px -15px rgba(12, 38, 29, 0.3)',
      },
      animation: {
        'scan': 'scan 2.5s ease-in-out infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'wave': 'wave 1.2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        scan: {
          '0%, 100%': { top: '0%' },
          '50%': { top: '100%' },
        },
        wave: {
          '0%': { height: '20%' },
          '100%': { height: '100%' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        }
      }
    },
  },
  plugins: [],
}
