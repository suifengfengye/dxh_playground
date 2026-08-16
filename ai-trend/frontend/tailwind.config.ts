import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(214.3 31.8% 91.4%)",
        background: "hsl(0 0% 100%)",
        foreground: "hsl(222.2 84% 4.9%)",
        muted: "hsl(210 40% 96.1%)",
        mutedForeground: "hsl(215.4 16.3% 46.9%)",
        primary: "hsl(222.2 47.4% 11.2%)",
        primaryForeground: "hsl(210 40% 98%)"
      }
    }
  },
  plugins: []
};

export default config;
