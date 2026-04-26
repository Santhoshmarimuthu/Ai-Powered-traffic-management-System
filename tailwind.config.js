/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary Colors
        'primary': '#2563EB', // blue-600
        'primary-foreground': '#FFFFFF', // white
        
        // Secondary Colors
        'secondary': '#64748B', // slate-500
        'secondary-foreground': '#FFFFFF', // white
        
        // Accent Colors
        'accent': '#FBBF24', // yellow-400
        'accent-foreground': '#0F172A', // slate-900
        
        // Background Colors
        'background': '#F8FAFC', // slate-50
        'surface': '#FFFFFF', // white
        
        // Text Colors
        'text-primary': '#0F172A', // slate-900
        'text-secondary': '#475569', // slate-600
        
        // Status Colors
        'success': '#059669', // emerald-600
        'success-foreground': '#FFFFFF', // white
        'warning': '#D97706', // amber-600
        'warning-foreground': '#FFFFFF', // white
        'error': '#DC2626', // red-600
        'error-foreground': '#FFFFFF', // white
        
        // Border Colors
        'border': '#E2E8F0', // slate-200
        'border-muted': '#F1F5F9', // slate-100
      },
      fontFamily: {
        'heading': ['Inter', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
        'caption': ['Inter', 'sans-serif'],
        'data': ['JetBrains Mono', 'monospace'],
      },
      fontWeight: {
        'normal': '400',
        'medium': '500',
        'semibold': '600',
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0, 0, 0, 0.1)',
        'modal': '0 4px 6px rgba(0, 0, 0, 0.1)',
      },
      borderRadius: {
        'DEFAULT': '8px',
      },
      transitionDuration: {
        '150': '150ms',
        '300': '300ms',
      },
      transitionTimingFunction: {
        'ease-out': 'ease-out',
        'ease-in-out': 'ease-in-out',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      zIndex: {
        '90': '90',
        '100': '100',
        '110': '110',
        '1000': '1000',
        '1100': '1100',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}