import tseslint from 'typescript-eslint'

export default [
    {
        ignores: ["dist/**", "node_modules/**","tsconfig.json", "vite.config.js"]
    },
    {
        files: ["**/*.ts", "**/*.tsx"],
        languageOptions: {
            parser: tseslint.parser,
        },
        plugins: {
            "@typescript-eslint": tseslint.plugin,
        },
        rules: {
            semi: ['error', 'always'],
            "@typescript-eslint/no-unused-vars": ['error']
        }
    },
    {
        files: ["**/*.js"],
        ignores: ["tsconfig.json", "vite.config.js", "eslint.config.js"],
        rules: {
            semi: ['error', 'always'],
            "no-console": ['error']
        },
    }
]