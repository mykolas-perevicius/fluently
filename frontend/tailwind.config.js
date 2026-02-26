/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', "system-ui", "-apple-system", "sans-serif"],
        display: ['"Inter Tight"', "system-ui", "sans-serif"],
        serif: ['"Lora"', "Georgia", "serif"],
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
        landing: {
          bg: "#060B14",
          surface: "#0F172A",
          border: "#1E293B",
          blue: "#006DC7",
          indigo: "#6366F1",
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
      animation: {
        ticker: "ticker 60s linear infinite",
        "float-slow": "floatSlow 20s ease-in-out infinite",
        "float-slow-alt": "floatSlowAlt 25s ease-in-out infinite",
        "float-slow-drift": "floatSlowDrift 30s ease-in-out infinite",
        "text-reveal": "textReveal 0.5s ease-out forwards",
      },
      keyframes: {
        ticker: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        floatSlow: {
          "0%, 100%": { transform: "translate(0, 0)" },
          "50%": { transform: "translate(30px, -40px)" },
        },
        floatSlowAlt: {
          "0%, 100%": { transform: "translate(0, 0)" },
          "50%": { transform: "translate(-25px, 35px)" },
        },
        floatSlowDrift: {
          "0%, 100%": { transform: "translate(0, 0)" },
          "33%": { transform: "translate(20px, -20px)" },
          "66%": { transform: "translate(-15px, 10px)" },
        },
        textReveal: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
