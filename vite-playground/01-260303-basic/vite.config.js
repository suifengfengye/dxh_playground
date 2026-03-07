import { defineConfig } from 'vite'
import VuePlugin from '@vitejs/plugin-vue'
import ReactPlugin from '@vitejs/plugin-react'

export default defineConfig({
    // plugins: [VuePlugin()],
    plugins: [ReactPlugin()],
    // resolve: {
    //     alias: {
    //         vue: 'vue/dist/vue.esm-bundler.js',
    //     },
    // },
})
