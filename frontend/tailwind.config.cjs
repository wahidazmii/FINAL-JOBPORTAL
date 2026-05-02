/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "forgotten-blue": "#1E2A3A",
        "jungle-teal": "#0D9488",
        "fountain-mint": "#DBF7EF",
        "portal-bg": "#F8FAFC",
      },
      fontFamily: {
        sans: ["Poppins", "sans-serif"],
        serif: ["DM Serif Display", "serif"],
      },
    },
  },
  plugins: [],
};
