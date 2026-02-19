/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        fluently: {
          50: "#f0f7ff",
          100: "#e0effe",
          200: "#b9dffd",
          300: "#7cc5fc",
          400: "#36a7f8",
          500: "#0c8de9",
          600: "#006fc7",
          700: "#0159a2",
          800: "#064c85",
          900: "#0b406e",
          950: "#072849",
        },
      },
    },
  },
  plugins: [],
};
