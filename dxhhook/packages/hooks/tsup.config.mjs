import { defineConfig } from 'tsup'

export default defineConfig({
    entry: ['src/index.ts'],
    format: ['esm', 'cjs'],
    outDir: 'es',
    dts: true,
    sourcemap: true,
    splitting: true,
    clean: true
})