/** @type {import('tailwindcss').Config} */

module.exports = {
  content: [
    './Wrapped2340/home/templates/**/*.html',  // Home app templates
    './Wrapped2340/users/templates/**/*.html', // Users app templates
    './Wrapped2340/slides/templates/**/*.html', // Slides app templates
    './Wrapped2340/common/templates/**/*.html', // Common app templates
    './Wrapped2340/**/templates/**/*.html',     // Catch-all for any other

   // app templates
    './static/**/*.css',                        // All static CSS files
    './static/js/**/*.js',                      // All static JS files
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/typography"),
    require('daisyui'),
  ],
  daisyui: {
    themes: true,
    styled: true,
    base: true,
  },
}


