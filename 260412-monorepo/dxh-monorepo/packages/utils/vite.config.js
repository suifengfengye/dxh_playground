import { defineConfig } from 'vite'

export default defineConfig({
    plugins: [],
    build: {
        lib: {
            entry: "./src/index.ts",
            name: "utils",
            formats: ["es", "cjs"]
        }
    }
})