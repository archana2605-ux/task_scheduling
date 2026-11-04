/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d7fe',
          300: '#a4bcfd',
          400: '#7a98fa',
          500: '#5572f5',
          600: '#3d52ea',
          700: '#2f3fd7',
          800: '#2b35ae',
          900: '#1e2470',
          950: '#0d1240',
        },
        rain: {
          none: '#f0f9ff',
          vlight: '#bae6fd',
          light: '#38bdf8',
          moderate: '#0284c7',
          heavy: '#1e40af',
          vheavy: '#7e22ce',
          extreme: '#be123c',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      }
    },
  },
  plugins: [],
}
