import { defineConfig } from 'vite'
import Vue from '@vitejs/plugin-vue'
import commonjs from 'vite-plugin-commonjs'

export default defineConfig({
    plugins: [Vue(), commonjs()],
    resolve: {
        alias: {
            "@": new URL('./src', import.meta.url).pathname,
        },
        extensions: [".ts", ".vue", ".d.ts"]
    },
    server: {
        port: 8080,
        host: '0.0.0.0',
        proxy: {
            "/api": {
                target: "http://127.0.0.1:3000",
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, '')
            }
        }
    }
})
