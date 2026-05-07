import { defineConfig } from 'eslint/config'
import tseslint from 'typescript-eslint'
import js from '@eslint/js'

export default defineConfig([
    {
        files: ["**/*.{js,jsx,ts,tsx}"],
        extends: [js.configs.recommended, ...tseslint.configs.recommended],
        rules: {
            "no-console": "error"
        },
        "languageOptions": {
            parser: tseslint.parser
        }
    }
])