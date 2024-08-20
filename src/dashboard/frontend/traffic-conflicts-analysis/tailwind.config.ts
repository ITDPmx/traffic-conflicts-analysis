import { type Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";

export default {
  content: ["./src/**/*.tsx"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-geist-sans)", ...fontFamily.sans],
        'fira-sans' : ["Fira Sans", "sans-serif"]
      },
      colors: {
        azul: "#0033a0",
        verde: "#00A94F",
        base: "#FFFFFF",
        gris: "#4D4D4D",
      },
      boxShadow: {
        'full-border': '0 0 10px rgba(0, 0, 0, 0.5)',
      }
    },
  },
  plugins: [],
} satisfies Config;
