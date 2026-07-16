/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#F8F9FC',
        foreground: '#1E293B',
        accent: '#6366F1',
        'accent-secondary': '#8B5CF6',
        muted: '#CBD5E1',
        'muted-foreground': '#64748B',
        border: '#E2E8F0',
        card: '#FFFFFF',
      },
    },
  },
  plugins: [],
}
