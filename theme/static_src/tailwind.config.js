/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        sand: {
          DEFAULT: '#C9A96E',
          dark: '#A8834A',
          light: '#D4B97E',
        },
        teal: {
          rm: '#2D7A7A',
          dark: '#1F5555',
          light: '#3A9A9A',
        },
        coral: '#E07E5D',
        cream: '#FAF8F2',
        'rm-dark': '#1A1A1A',
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', '"Times New Roman"', 'serif'],
      },
    },
  },
  plugins: [],
}
