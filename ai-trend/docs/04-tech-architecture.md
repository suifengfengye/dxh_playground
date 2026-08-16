# GitHub AI Trend MVP 技术方案

## 1. 方案结论

针对当前的最小可行产品目标：

- 手动输入 GitHub 仓库地址加入 watchlist
- 保存仓库当前 stars / forks / subscribers 等指标
- 定时采集每日快照
- 用折线图展示趋势
- 提供基础的增长判断和爆发预警

推荐采用下面这套更轻量、更适合个人项目的技术方案：

- 后端：`Python + FastAPI`
- 前端：`Next.js + TypeScript + shadcn/ui`
- 数据库：`SQLite`
- 定时采集：后端内置 `APScheduler`，后续可拆独立任务
- 仓库组织：`monorepo`
- 部署：`Docker 镜像 + Docker Compose`

这套方案的核心特点是：

- 技术栈足够现代，开发体验好
- 学习和维护成本低
- 对小服务器更友好
- 能很快做出可上线的 MVP

## 2. 为什么这样选

### 2.1 后端：Python + FastAPI

选择理由：

- 已经有 Python demo，可以直接复用 GitHub API 访问逻辑
- FastAPI 开发 API 很快，自带 OpenAPI 文档
- 后续如果加趋势分析、异常检测、周报生成，Python 更顺手
- 对单人项目来说，开发效率和调试体验都很好

后端主要负责：

- 解析 GitHub 仓库地址
- 调用 GitHub 官方 API 拉取仓库当前指标
- 保存仓库基础信息和每日快照
- 提供 watchlist、仓库详情、趋势图接口
- 定时采集每日快照
- 计算简单的增长和预警指标

### 2.2 前端：Next.js + TypeScript + shadcn/ui

选择理由：

- Next.js 很适合做 dashboard、列表页、详情页
- TypeScript 更适合长期维护
- `shadcn/ui` 组件清爽、可控、不重
- 配合 Tailwind，可以很快搭一个看起来干净的管理后台

`shadcn/ui` 很适合这个项目的原因：

- 列表、表单、弹窗、Tabs、Badge、Card 都有成熟模式
- 可以组合出 watchlist 面板和 repo 详情页
- 不会像重型 UI 库一样给小项目带来过多包袱

建议前端图表库：

- 首选：`ECharts`
- 备选：`Recharts`

如果后续趋势分析更复杂、对比图更多，优先用 `ECharts`。

### 2.3 数据库：SQLite

当前阶段推荐 SQLite，而不是 PostgreSQL。

原因：

- 你的服务器配置小，SQLite 更省资源
- MVP 数据量不会很大，完全够用
- 无需额外部署独立数据库服务
- Docker 化也更轻
- 本地开发和部署环境更容易保持一致

这个项目第一版的数据规模通常只有：

- 几十到几百个仓库
- 每天一次采集
- 每个仓库每天一条快照

按这个量级，SQLite 完全足够。

### 2.4 部署：Docker + Docker Compose

推荐继续使用 Docker，但数据库不再单独起容器。

推荐方式：

- `web` 一个容器
- `api` 一个容器
- SQLite 文件挂载为 volume

优点：

- 部署简单
- 占用资源少
- 搬迁服务器方便
- 适合个人项目和 MVP

## 3. monorepo 结构设计

推荐采用简单 monorepo，不需要一开始引入过重的构建工具。

目录建议：

```text
ai-trend-app/
  backend/
    app/
    tests/
    pyproject.toml
    uv.lock
    Dockerfile
  frontend/
    app/
    components/
    lib/
    package.json
    Dockerfile
  infra/
    docker/
  data/
    app.db
  docker-compose.yml
  .env.example
  README.md
```

说明：

- `backend/`：FastAPI 项目
- `frontend/`：Next.js 项目
- `data/`：SQLite 数据文件目录
- `infra/`：部署和环境脚本

## 4. 后端技术设计

### 4.1 后端推荐依赖

推荐核心依赖：

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `alembic`
- `pydantic`
- `httpx`
- `apscheduler`

如果后面要做更完整的数据处理，可再加：

- `pandas`
- `numpy`

但 MVP 第一版可以不加，避免依赖过重。

### 4.2 后端模块结构

```text
backend/
  app/
    api/
      watchlist.py
      repos.py
      metrics.py
      dashboard.py
    core/
      config.py
    db/
      base.py
      session.py
    models/
      repository.py
      daily_metric.py
    schemas/
      watchlist.py
      repo.py
      metric.py
    services/
      github_service.py
      watchlist_service.py
      metric_service.py
      analysis_service.py
    jobs/
      collect_daily_metrics.py
    main.py
```

### 4.3 MVP API 设计

#### Watchlist

- `POST /watchlist`
  - 输入 GitHub 仓库地址
  - 解析并拉取仓库基础信息
  - 保存到数据库

- `GET /watchlist`
  - 返回当前 watchlist 列表

- `DELETE /watchlist/{repo_id}`
  - 从 watchlist 中移除

#### Repo

- `GET /repos/{repo_id}`
  - 返回仓库基础信息

- `GET /repos/{repo_id}/metrics`
  - 返回某个仓库的历史趋势数据

- `POST /repos/{repo_id}/collect`
  - 手动触发一次采集

#### Dashboard

- `GET /dashboard/summary`
  - 返回总仓库数、最近采集时间、近 7 天热点等

- `GET /dashboard/top-growing`
  - 返回最近增长较快的仓库

### 4.4 定时任务方案

第一版建议用内置调度：

- `APScheduler`

理由：

- 实现简单
- 适合小项目
- 不需要额外引入 Celery / Redis

调度策略建议：

- 每天固定时间采集一次全量 watchlist
- 同时支持单仓库手动采集

后续如果项目变大，再考虑拆成独立 worker。

## 5. 数据库设计

由于使用 SQLite，表结构上仍然保持关系型设计，但尽量简单。

### 5.1 `repositories`

存仓库主数据。

字段建议：

- `id`
- `owner`
- `name`
- `full_name`
- `repo_url`
- `description`
- `language`
- `default_branch`
- `stars_current`
- `forks_current`
- `subscribers_current`
- `open_issues_current`
- `topics_json`
- `is_active`
- `created_at`
- `updated_at`

### 5.2 `daily_metrics`

存每日快照。

字段建议：

- `id`
- `repository_id`
- `metric_date`
- `stars`
- `forks`
- `subscribers`
- `open_issues`
- `pushed_at`
- `raw_payload_json`
- `created_at`

约束建议：

- `UNIQUE(repository_id, metric_date)`

### 5.3 关于 watch 字段

GitHub API 中要特别注意：

- `stargazers_count`：star 总数
- `forks_count`：fork 总数
- `watchers_count`：通常与 star 一样，不建议作为真实 watch 指标
- `subscribers_count`：更接近真实的 watch/订阅人数

因此数据库和页面字段建议统一使用：

- `stars`
- `forks`
- `subscribers`

而不要在产品层直接展示 `watchers_count`。

## 6. 前端技术设计

### 6.1 页面规划

MVP 建议只做 4 个页面：

1. 首页 / Dashboard
2. Watchlist 页
3. Repo 详情页
4. Add Repo 弹窗或单独页面

### 6.2 页面内容建议

#### Dashboard

- watchlist 总数
- 今日采集状态
- 最近 7 天增长较快的仓库
- 最近更新活跃仓库

#### Watchlist

- 仓库卡片或表格
- stars / forks / subscribers 当前值
- 7d 增量
- 最近更新时间
- 删除按钮

#### Repo 详情

- 仓库基础信息
- stars/forks/subscribers 折线图
- 最近 7d / 30d 增量
- 最近 push 时间

### 6.3 组件建议

基于 `shadcn/ui` 建议优先使用：

- `Card`
- `Table`
- `Button`
- `Badge`
- `Tabs`
- `Dialog`
- `Input`
- `Form`
- `Skeleton`

## 7. 依赖管理：requirements.txt 是否落后

**结论：**

- `requirements.txt` 不是不能用
- 但对于新项目来说，通常不再是首选

### 7.1 为什么说它有点旧

`requirements.txt` 的问题主要在于：

- 只能表达“装哪些包”
- 不能很好表达项目元数据
- 依赖分组管理不够优雅
- 锁版本和开发依赖管理体验一般

例如你很难优雅地区分：

- 运行依赖
- 开发依赖
- 测试依赖
- lint 依赖

### 7.2 更推荐什么

对于这个项目，我更推荐：

- `pyproject.toml`
- 配合 `uv` 管理依赖

推荐原因：

- 现在 Python 新项目越来越多转向 `pyproject.toml`
- `uv` 很快，体验好，锁文件清晰
- 更适合长期维护

推荐组合：

- `pyproject.toml`
- `uv.lock`

### 7.3 MVP 建议

后端建议使用：

- `pyproject.toml` 管依赖
- `uv` 负责安装和锁版本

也就是说：

- 不建议把 `requirements.txt` 作为主方案
- 如果后续部署需要兼容某些平台，可以额外导出一份 requirements，但不是主入口

## 8. 部署方案

### 8.1 Docker Compose 方案

第一版建议：

- 一个 `api` 容器
- 一个 `web` 容器
- SQLite 文件通过 volume 挂载

示意：

```yaml
services:
  api:
    build: ./backend
    volumes:
      - ./data:/app/data
    env_file:
      - .env

  web:
    build: ./frontend
    env_file:
      - .env
    depends_on:
      - api
```

### 8.2 部署注意点

- SQLite 文件目录一定要做持久化挂载
- 注意单机部署下 SQLite 只适合中低并发场景
- MVP 阶段完全可接受

### 8.3 后续升级路径

如果未来用户量上来，可以逐步升级：

1. SQLite -> PostgreSQL
2. APScheduler -> 独立 worker
3. Docker Compose -> 更正式的容器编排

这也是当前方案的优点：

- 先轻量上线
- 后续可平滑演进

## 9. 最终建议

当前这个项目的最优技术方案，建议确定为：

- 后端：`Python + FastAPI`
- 前端：`Next.js + TypeScript + shadcn/ui`
- 数据库：`SQLite`
- 依赖管理：`pyproject.toml + uv`
- 仓库组织：简单 `monorepo`
- 部署：`Docker + Docker Compose`

这个方案非常适合：

- 单人开发
- 小服务器部署
- 低成本 MVP 验证

而且和你的项目目标也高度匹配：

- 先把 watchlist + 趋势图跑通
- 再逐步加分析、预警和内容辅助能力

## 10. 下一步建议

按这个方案，下一步可以直接开始做项目骨架：

1. 初始化 monorepo 目录
2. 创建 FastAPI 后端
3. 创建 Next.js 前端
4. 用 SQLite 建 `repositories` 和 `daily_metrics`
5. 先完成 `POST /watchlist`
6. 前端完成“添加仓库 + 列表展示”

等这一步跑通，整个 MVP 就真正进入开发阶段了。
