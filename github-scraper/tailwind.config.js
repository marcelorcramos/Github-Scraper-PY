/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx}", 
    "./src/components/**/*.{js,ts,jsx,tsx}", 
  ],
  theme: {
    extend: {
      colors: {
        dark: "#141313",
        gray: "#A5A5A5",
        lightDark: "#333131",
      },
    },
  },
  plugins: [],
};