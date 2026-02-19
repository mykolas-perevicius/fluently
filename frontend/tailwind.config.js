/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', "system-ui", "-apple-system", "sans-serif"],
        display: ['"Inter Tight"', "system-ui", "sans-serif"],
      },
      colors: {
        glass: {
          surface: "rgba(30,41,59,0.4)",
          border: "rgba(255,255,255,0.1)",
          hover: "rgba(255,255,255,0.05)",
        },
        accent: {
          cyan: "#06b6d4",
          purple: "#8b5cf6",
        },
      },
      borderRadius: {
        "2xl": "16px",
        "3xl": "24px",
      },
      boxShadow: {
        glass: "0 8px 32px rgba(0,0,0,0.3)",
        "glow-cyan": "0 0 15px rgba(6,182,212,0.1)",
        "glow-purple": "0 0 10px rgba(139,92,246,0.2)",
      },
      backdropBlur: {
        glass: "10px",
      },
    },
  },
  plugins: [],
};
