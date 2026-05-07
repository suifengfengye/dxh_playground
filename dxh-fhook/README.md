
- 构建工具：tsup
- 文档工具：rspress
- 框架: react 19/typescript/pnpm workspace/turborepo
- 测试工具: Vitest/React Testing Library(RTL)

# 1. pnpm workspace构建

创建 pnpm-workspace.yaml 文件

```yaml
packages:
  - "packages/*"
  - "apps/*"
```

# 2. eslint

- eslint
- typescript-eslint
- recommended: @eslint/js.configs.recommended, tseslint.configs.recommended
- globals: 告诉eslint哪些变量是外部环境提供的全局变量，不应该报错。
- prettier: eslint-plugin-prettier
- lint-staged: 只校验git staged中的文件
- cspell: 拼写处理 