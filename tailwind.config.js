/** @type {import('tailwindcss').Config} */

module.exports = {
  content: [
      './users/templates/users/*.html',
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/js/**/*.js',
  ],
  daisyui: {
    themes: ["light", "dark", "cupcake"],
  },
  theme: {
    extend: {},
  },
  plugins: [
      require('daisyui'),
  ],
}


