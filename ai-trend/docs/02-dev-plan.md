# GitHub AI Trend 工具开发方案与结构设计

## 1. 产品定位

### 1.1 产品目标

做一个专门面向 AI 开源仓库的趋势监控工具，帮助用户：

- 跟踪指定仓库的 stars/forks/watchers 等指标
- 看增长曲线，而不是只看总量
- 发现“可能要爆”的项目
- 支持仓库、主题、生态级别的对比分析

### 1.2 MVP 边界

先只解决最核心的问题：

- 支持手动维护观察名单
- 每天自动采集 GitHub 指标
- 前端展示趋势图和仓库详情
- 给出基础增长信号和简单预警

暂时不做：

- 自动全网爬取所有 AI 仓库
- 复杂推荐算法
- 登录、权限、多用户协作
- 高频实时更新

## 2. 整体架构

推荐采用：

- 后端：Python + FastAPI
- 定时采集：APScheduler / cron
- 数据存储：PostgreSQL
- 缓存：Redis（可选）
- 前端：Next.js + ECharts
- 部署：Docker Compose

整体结构：

```text
GitHub API / OSS Insight
        |
        v
  Collector Layer
        |
        v
  Metrics Database
        |
        v
  Analysis Service
        |
        v
 FastAPI Backend
        |
        v
 Next.js Dashboard
```

## 3. 数据源设计

### 3.1 数据源分层

建议分成两类：

#### A. 官方实时快照源

- GitHub REST API

用途：

- 当前 stars
- forks
- watchers/subscribers
- open issues
- 更新时间
- topics

#### B. 历史回填分析源

- OSS Insight API

用途：

- 冷启动时回填仓库历史 star 曲线
- 对已知热门仓库做历史分析页

### 3.2 数据策略

产品应该采用“双轨策略”：

1. 从今天开始，自己保存每日快照。
2. 对历史部分，能从 OSS Insight 回填的就回填，回填不了就从创建日开始自然积累。

这样可以避免未来再次受第三方限制。

## 4. 核心功能设计

## 4.1 观察名单管理

用户可维护：

- 仓库名称
- 分类
- 标签
- 是否启用监控
- 数据源类型

示例分类：

- Agent Framework
- Coding Agent
- Browser Agent
- Protocol
- RAG
- Tooling

## 4.2 每日指标采集

每天运行一次采集任务，拉取：

- stars
- forks
- watchers_count
- subscribers_count
- open_issues_count
- pushed_at

并保存为每日快照。

## 4.3 趋势分析

后端计算：

- 1d 增量
- 7d 增量
- 30d 增量
- 7d/30d 增速
- 增长加速度
- fork/star 比
- 活跃度信号

## 4.4 爆发预警

定义一个简单的 breakout score。

例如：

```text
breakout_score =
0.40 * 7d_star_growth_rate
+ 0.25 * acceleration_7d_vs_30d
+ 0.15 * fork_growth_rate
+ 0.10 * activity_score
+ 0.10 * engagement_score
```

输出标签：

- 稳定增长
- 加速增长
- 异常上升
- 爆发候选

## 4.5 页面展示

前端最小页面建议：

1. 仪表盘
2. 仓库详情页
3. 对比页
4. 观察名单页

## 5. 数据库结构设计

推荐最小表结构如下。

## 5.1 `repositories`

存仓库主数据。

字段建议：

- `id`
- `owner`
- `name`
- `full_name`
- `display_name`
- `category`
- `description`
- `homepage_url`
- `repo_url`
- `language`
- `license`
- `topics_json`
- `source_type` (`github`, `ossinsight_backfill`, `manual`)
- `is_active`
- `created_at`
- `updated_at`

## 5.2 `daily_metrics`

存每日快照。

字段建议：

- `id`
- `repository_id`
- `metric_date`
- `stars`
- `forks`
- `watchers`
- `subscribers`
- `open_issues`
- `pushed_at`
- `raw_payload_json`
- `created_at`

约束建议：

- `UNIQUE(repository_id, metric_date)`

## 5.3 `analysis_snapshots`

存分析结果，避免每次临时计算。

字段建议：

- `id`
- `repository_id`
- `metric_date`
- `star_delta_1d`
- `star_delta_7d`
- `star_delta_30d`
- `star_growth_rate_7d`
- `star_growth_rate_30d`
- `acceleration_score`
- `fork_growth_rate`
- `activity_score`
- `breakout_score`
- `signal_level`
- `created_at`

## 5.4 `collections`

用于主题集合和生态集合。

字段建议：

- `id`
- `name`
- `slug`
- `description`
- `collection_type` (`topic`, `ecosystem`, `manual`)

## 5.5 `collection_repositories`

集合与仓库的关联关系。

- `id`
- `collection_id`
- `repository_id`

## 6. 后端模块设计

推荐目录结构：

```text
backend/
  app/
    api/
      repos.py
      metrics.py
      collections.py
      dashboard.py
    collectors/
      github_repo_collector.py
      ossinsight_backfill.py
    analysis/
      growth.py
      breakout.py
      ranking.py
    models/
      repository.py
      daily_metric.py
      analysis_snapshot.py
    services/
      repo_service.py
      metric_service.py
      analysis_service.py
    scheduler/
      jobs.py
    db/
      session.py
      base.py
    main.py
```

### 6.1 Collector 层

职责：

- 调 GitHub API
- 拉取仓库实时快照
- 拉取 OSS Insight 历史数据
- 标准化数据结构

### 6.2 Analysis 层

职责：

- 计算增长率
- 计算 breakout score
- 生成排行榜
- 生成趋势摘要

### 6.3 API 层

建议提供：

- `GET /repos`
- `GET /repos/{id}`
- `GET /repos/{id}/metrics`
- `GET /repos/{id}/analysis`
- `GET /dashboard/top-growing`
- `GET /collections`
- `GET /collections/{id}/ranking`

## 7. 前端结构设计

推荐目录：

```text
frontend/
  app/
    page.tsx
    repos/[id]/page.tsx
    compare/page.tsx
    watchlist/page.tsx
  components/
    trend-chart.tsx
    growth-badge.tsx
    repo-card.tsx
    stat-kpi.tsx
    compare-table.tsx
  lib/
    api.ts
    format.ts
```

### 7.1 仪表盘模块

展示：

- 今日新增监控仓库数
- 近 7 日增长最快的仓库
- 爆发候选榜
- 分类分布

### 7.2 仓库详情页

展示：

- 仓库简介
- stars/forks/watchers 指标
- 趋势图
- 7d/30d 增长
- breakout score
- 同类仓库对比入口

### 7.3 对比页

支持：

- 多仓库趋势曲线
- 时间对齐对比
- 指标选择切换

## 8. 算法与信号设计

MVP 不建议上复杂机器学习，规则模型足够。

### 8.1 基础规则

判定“增长异常”：

- `7d star delta > 30d average * 2`
- 或 `7d growth rate` 超过某阈值

判定“爆发候选”：

- 连续 2 个采集周期增长加速
- forks 同步增长
- 最近 14 天有活跃提交

### 8.2 后续可升级方向

- 异常检测：EWMA / z-score
- 分组基线：按类别单独建阈值
- 事件解释：结合 release、blog、HN、X 等外部事件

## 9. 可行性与工程风险

## 9.1 可行点

- 每日快照监控完全可做。
- Python + FastAPI + cron 足够支撑 MVP。
- 前端图表展示也非常标准。

## 9.2 风险点

### 数据源风险

- GitHub 原生历史 star 明细受限。
- 第三方历史接口未来也可能变化。

解决：

- 自建快照库是主方案。
- 第三方只用于 backfill。

### 监控对象抽象风险

- 协议型项目无法用单仓库完全代表。

解决：

- 加 `collection` 机制。

### 指标误判风险

- 某些仓库短期被营销带火，但长期价值不高。

解决：

- 页面中同时展示增长和维护活跃度，不只看 stars。

## 10. 分阶段开发计划

## Phase 1：MVP（1-2 周）

目标：

- 手动维护 20-50 个仓库
- 每日采集 GitHub 快照
- 前端展示趋势图和排行

交付：

- 仓库列表页
- 仓库详情页
- 每日任务
- PostgreSQL 表结构

## Phase 2：量化分析（第 3 周）

目标：

- 增加 7d/30d 增长率
- breakout score
- 分类排行

## Phase 3：历史回填（第 4 周）

目标：

- 接入 OSS Insight backfill
- 给热门仓库生成历史曲线

## Phase 4：增强版（后续）

- 主题集合监控
- 异常推送
- RSS/邮件/飞书通知
- 内容创作者选题榜单

## 11. 最终建议

这个项目值得做，但建议把目标收窄成：

> 一个面向 AI 开源仓库的轻量趋势监控与爆发预警工具

不要一开始把自己做成“GitHub 全量分析平台”。

最优先的价值是：

- 帮你自己和类似用户节省盯趋势的时间
- 形成结构化的 AI 开源观察样本库
- 后续还能和技术内容创作、自媒体选题、行业分析结合

从产品和开发成本的平衡上看，这是一个很适合先做 MVP 的方向。
