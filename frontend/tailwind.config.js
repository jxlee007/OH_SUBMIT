/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    screens: {
      'sm': '375px',   // Mobile breakpoint (Odoo requirement: 375px)
      'md': '768px',   // Tablet breakpoint (Odoo requirement: 768px)
      'lg': '1280px',  // Desktop breakpoint (Odoo requirement: 1280px)
    },
    extend: {
      colors: {
        brand: {
          50: '#f5f3ff',
          100: '#ede9fe',
          500: '#7c3aed',
          600: '#6d28d9',
          700: '#5b21b6',
        },
        odoo: {
          purple: '#714B67',
          teal: '#017E84',
          dark: '#1C2434',
        }
      }
    },
  },
  plugins: [],
}

