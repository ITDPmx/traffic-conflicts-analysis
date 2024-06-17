import { type Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";

export default {
  content: ["./src/**/*.tsx"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-geist-sans)", ...fontFamily.sans],
      },
      colors: {
        azul: "#0033a0",
        verde: "#41a85d",
        base: "#FFFFFF",
      }
    },
  },
  plugins: [],
} satisfies Config;
