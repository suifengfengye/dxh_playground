- 构建工具：tsup
- 文档工具：rspress
- 框架: react 19/typescript/pnpm workspace/turborepo
- 测试工具: Vitest/React Testing Library(RTL)

# 1. pnpm workspace构建

创建 pnpm-workspace.yaml 文件

```yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

# 2. eslint

- eslint：处理代码规范，包含有质量检查。
- typescript-eslint
- eslint-plugin-simple-import-sort: 处理导入排序规范
- recommended: @eslint/js.configs.recommended, tseslint.configs.recommended
- globals: 告诉eslint哪些变量是外部环境提供的全局变量，不应该报错。globas就是一个json配置。

vscode插件:ESLint

# 3. prettier

处理代码格式化。

- eslint-config-prettier: 关闭和Prettier冲突的ESlint规则。
- eslint-plugin-prettier: 把Prettier当成ESLint规则执行。

vscode插件: Prettier

# 4. lint-staged

只校验git staged中的文件

```json
{
  "lint-staged": {
    "**/*.{js,jsx}": ["eslint --fix", "prettier --cache --write"],
    "**/*.{ts,tsx}": ["eslint --fix", "prettier --cache --write --parser=typescript"]
  }
}
```

执行的命令:

```shell
npx lint-staged
```

# 5. cspell: 拼写处理

配置文件 cspell.json

```json
{
  "import": "@cspell/dict-lorem-ipsum/cspell-ext.json",
  "caseSensitive": false,
  "dictionaries": ["miaoma-words"],
  "dictionaryDefinitions": [
    {
      "name": "miaoma-words",
      "path": "./.cspell/miaoma-words.txt",
      "addWords": true
    }
  ],
  "ignorePaths": ["**/node_modules/**", "**/dist/**"]
}
```

命令：

```shell
"spellcheck":"cspell lint --dot --gitignore --color --cache --show-suggestions \"(packages|apps)/**/*.@(html|js|cjs|mjs|ts|tsx|css|scss|md)\""
```

vscode插件: Code Spell Checker

# 6. 提交校验

- commitlint
- commitizen
- cz-git
- husky

scripts脚本配置:

```json
{
  "scripts": {
    "commit": "cz-git"
  },
  "config": {
    "commitizen": {
      "path": "cz-git"
    }
  }
}
```

cz-git的配置文件：commitlint.config.js

husky 初始化命令：
```shell
# 执行后，会在项目根目录下生成.husky/pre-commit文件，里面可以编写提交前进行校验的命令
npx husky init
```

```bash
# 1. spellcheck
pnpm spellcheck
# 2. lint
pnpm lint
```