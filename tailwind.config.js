/** @type {import('tailwindcss').Config} */

module.exports = {
  content: [
    './Wrapped2340/home/templates/**/*.html',  // Home app templates
    './Wrapped2340/users/templates/**/*.html', // Users app templates
    './Wrapped2340/slides/templates/**/*.html', // Slides app templates
    './Wrapped2340/**/templates/**/*.html',     // Catch-all for any other

   // app templates
    './static/**/*.css',                        // All static CSS files
    './static/js/**/*.js',                      // All static JS files
  ],
  daisyui: {
    themes: [
      "light",
      "dark",
      "cupcake",
      "bumblebee",
      "emerald",
      "corporate",
      "synthwave",
      "retro",
      "cyberpunk",
      "valentine",
      "halloween",
      "garden",
      "forest",
      "aqua",
      "lofi",
      "pastel",
      "fantasy",
      "wireframe",
      "black",
      "luxury",
      "dracula",
      "cmyk",
      "autumn",
      "business",
      "acid",
      "lemonade",
      "night",
      "coffee",
      "winter",
      "dim",
      "nord",
      "sunset",
    ],

    base: true,
  },
  theme: {
    extend: {},
  },
  plugins: [
      require('daisyui'),
  ],
}


