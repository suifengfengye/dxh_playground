import { defineConfig } from 'eslint/config'
import tseslint from 'typescript-eslint'
import js from '@eslint/js'
import globals from 'globals'
import simpleImportSort from 'eslint-plugin-simple-import-sort'
import prettier from 'eslint-plugin-prettier'

export default defineConfig([
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    rules: {
      'no-console': 'error',
      'simple-import-sort/imports': 'error',
      'simple-import-sort/exports': 'error',
      'prettier/prettier': 'error'
    },
    plugins: {
      'simple-import-sort': simpleImportSort,
      prettier: prettier
    },
    languageOptions: {
      parser: tseslint.parser,
      globals: {
        ...globals.browser
      }
    }
  }
])
