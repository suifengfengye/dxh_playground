# GitHub AI Trend 需求调研与量化分析

## 1. 问题定义

`idea.md` 里的核心问题不是“看今天哪些仓库火”，而是想回答两件事：

1. 一个 AI 技术或开源仓库在爆火前，有没有可量化的前置信号。
2. 能不能做一个小工具，持续监控这些信号，帮助上班忙、没时间盯趋势的人尽早发现值得关注的项目。

这类工具的目标用户很明确：

- AI 从业者：想知道最近值得投入学习的方向。
- 技术内容创作者：想尽早发现有传播潜力的话题。
- 开发者/架构师：想判断一个协议、框架、Agent 平台是不是进入加速期。
- 投资/行业研究人员：想做开源热度与生态成熟度的早期判断。

## 2. 需求拆解

### 2.1 核心需求

- 维护一个 AI 相关仓库观察名单。
- 每天采集 GitHub 仓库指标。
- 展示趋势曲线，而不是只展示当前总星数。
- 给出“增长异常”和“可能爆发”的信号。
- 支持仓库对比和分类对比。

### 2.2 隐含需求

- 不只是监控单仓库，还要支持“协议/生态”级别监控。
- 需要有历史回填能力，否则新产品冷启动时没有历史数据。
- 要明确“GitHub Trending”和“长期价值”的区别。

## 3. 监控对象设计

不是所有热点都适合用“单个仓库”来表示，建议把监控对象分成 4 类：

1. 单仓库
   - 例如 `langgenius/dify`
   - 适合产品型平台、Agent 应用、RAG 产品。
2. 主仓库 + 官方 SDK/样例仓库
   - 例如 `a2aproject/A2A` + `a2aproject/a2a-python`
   - 适合协议型项目。
3. 生态集合
   - 例如 MCP 不只看一个仓库，而看 `servers`、SDK、awesome 列表、样板项目。
4. 主题集合
   - 例如“浏览器自动化 Agent”“Coding Agent”“RAG Engine”
   - 适合后续做榜单和专题页。

## 4. 候选技术/仓库补充

在 `idea.md` 原始名单基础上，建议补充：

- MCP：`modelcontextprotocol/servers` 作为代表仓库，后续应升级为生态监控。
- A2A：`a2aproject/A2A`
- Dify：`langgenius/dify`
- RAGFlow：`infiniflow/ragflow`
- OpenClaw：`openclaw/openclaw`
- OpenHands
- browser-use
- Stagehand
- Continue
- Aider
- LangFlow
- Flowise
- LightRAG
- Mem0
- Claude Code/OpenAI Codex 一类开源相关生态仓库

结论：MCP、A2A 这类“协议”和 Dify、RAGFlow 这类“产品平台”应该分开分析，前者更适合看生态扩散，后者更适合看主仓库爆发。

## 5. 可获取数据源调研

### 5.1 GitHub 原生 API 能拿到什么

GitHub REST API 可以稳定拿到仓库当前快照指标，例如：

- `stargazers_count`
- `forks_count`
- `watchers_count`
- `subscribers_count`
- `open_issues_count`
- `created_at`
- `pushed_at`
- topics、language、license

官方文档：

- Repository API: https://docs.github.com/rest/repos/repos
- Starring API: https://docs.github.com/rest/activity/starring

### 5.2 GitHub 原生 API 的限制

最关键限制：2026 年 7 月后，GitHub 对公开仓库的 stargazers 明细接口增加了访问限制。对“你不是管理员/协作者”的公开仓库，外部服务已经不能稳定读取完整的加星时间明细。

参考：

- GitHub Starring API 文档变更说明：
  https://docs.github.com/rest/activity/starring
- Star History 官方说明：
  https://www.star-history.com/blog/github-stargazer-api-restriction/

这意味着：

- 你不能只靠 GitHub 原生 API，就给任意公开仓库做完整历史 star 曲线重建。
- 你的产品如果现在开始做，最可靠的方式是“从今天开始自己建日快照库”。

### 5.3 可行的补充数据源

#### OSS Insight

OSS Insight 提供公开 API，可以直接拿仓库的历史 stargazers 曲线，支持按 `day/week/month` 聚合。

接口文档：

- https://ossinsight.io/docs/api/stargazers-history/

优势：

- 公共可访问。
- 已有历史数据，适合冷启动和历史分析。
- 能覆盖很多 AI 仓库。

限制：

- 它不是 GitHub 官方数据源，属于第三方分析层。
- 部分仓库数据会有延迟。
- 对协议/生态分析仍然需要自己定义监控集合。

## 6. 量化指标体系

建议把指标分为 3 层：

### 6.1 基础指标

- stars
- forks
- watchers_count
- subscribers_count
- open_issues_count
- push recency（最近一次提交时间）

### 6.2 增长指标

- 日增 stars
- 7 日 stars 增长率
- 30 日 stars 增长率
- forks/stars 比值
- subscribers/stars 比值
- issue 增长速度

### 6.3 爆发信号指标

建议定义一个 `breakout_score`，例如：

- `7d_star_growth_rate`
- `7d_vs_30d_acceleration`
- `fork_growth_rate`
- `recent_push_frequency`
- `issue_discussion_heat`

可做一个简单加权分数：

```text
breakout_score =
0.40 * normalized(7d_star_growth_rate)
+ 0.25 * normalized(star_acceleration)
+ 0.15 * normalized(fork_growth_rate)
+ 0.10 * normalized(active_maintainer_signal)
+ 0.10 * normalized(issue_discussion_heat)
```

## 7. 典型样本量化分析

以下分析主要用于验证 idea 是否成立，不追求学术严谨，更关注“爆火前能否看到信号”。

### 7.1 Dify

数据源：

- OSS Insight stargazers history:
  https://api.ossinsight.io/v1/repos/langgenius/dify/stargazers/history/?per=month&from=2023-01-01&to=2026-08-01

关键样本：

| 时间 | 累计 Stars |
|---|---:|
| 2023-04-01 | 17 |
| 2023-05-01 | 3,714 |
| 2024-04-01 | 24,512 |
| 2025-02-01 | 71,398 |
| 2026-08-01 | 111,568 |

结论：

- Dify 在项目上线第一个月就出现了明显放量，不是慢热型。
- 2024 Q2 和 2025 Q1 都出现过大幅跃升，说明这类平台型产品会有多轮增长波峰。
- 对这类仓库，单看总 stars 不够，必须看“多轮增长加速度”。

### 7.2 RAGFlow

数据源：

- OSS Insight stargazers history:
  https://api.ossinsight.io/v1/repos/infiniflow/ragflow/stargazers/history/?per=month&from=2023-12-01&to=2026-08-01

关键样本：

| 时间 | 累计 Stars |
|---|---:|
| 2024-04-01 | 5,619 |
| 2024-12-01 | 25,019 |
| 2025-02-01 | 38,730 |
| 2025-03-01 | 44,081 |
| 2026-08-01 | 61,513 |

结论：

- RAGFlow 是“中早期稳定增长 + 某一阶段突然加速”的典型。
- 2025 Q1 的斜率明显变陡，适合被工具识别为“进入爆发窗口”。

### 7.3 MCP 代表仓库：modelcontextprotocol/servers

数据源：

- OSS Insight stargazers history:
  https://api.ossinsight.io/v1/repos/modelcontextprotocol/servers/stargazers/history/?per=month&from=2024-11-01&to=2026-08-01

关键样本：

| 时间 | 累计 Stars |
|---|---:|
| 2024-11-01 | 2,774 |
| 2025-02-01 | 10,306 |
| 2025-03-01 | 25,491 |
| 2025-04-01 | 38,056 |
| 2026-08-01 | 60,594 |

结论：

- MCP 的代表仓库在 2025 年 3-4 月出现爆炸式增长。
- 协议型项目往往会伴随生态仓库一起放量，所以只看一个仓库容易低估真实热度。

### 7.4 A2A

数据源：

- OSS Insight stargazers history:
  https://api.ossinsight.io/v1/repos/a2aproject/A2A/stargazers/history/?per=month&from=2025-01-01&to=2026-08-01
- GitHub 公开主页与组织页资料：
  https://github.com/a2aproject/A2A
  https://github.com/a2aproject

关键样本：

| 时间 | 累计 Stars |
|---|---:|
| 2025-04-01 | 12,370 |
| 2025-05-01 | 14,431 |
| 2026-01-01 | 17,343 |
| 2026-07-01 | 17,834 |

补充信息：

- OSS Insight 在 2026-03 的议题里记录主仓库已到 `22.7k` stars。

结论：

- A2A 更像“协议发布即爆发”的项目，而不是靠长尾扩散慢慢起量。
- 这类项目需要结合 SDK、示例仓库和生态扩展一起监控。

### 7.5 OpenClaw

数据源：

- OSS Insight stargazers history:
  https://api.ossinsight.io/v1/repos/openclaw/openclaw/stargazers/history/?per=month&from=2025-11-01&to=2026-08-01
- GitHub 仓库主页：
  https://github.com/openclaw/openclaw

关键样本：

| 时间 | 累计 Stars |
|---|---:|
| 2025-11-01 | 90 |
| 2025-12-01 | 381 |
| 2026-01-01 | 42,840 |
| 2026-02-01 | 76,852 |
| 2026-03-01 | 99,597 |
| 2026-08-01 | 105,714 |

结论：

- 这是典型的超病毒式项目。
- 爆发前并没有很长的酝酿期，更多依赖强传播事件和高讨论度。
- 这类项目对工具提出更高要求：要能识别“瞬时异常”，不是只看月度趋势。

## 8. 从样本里得到的规律

### 8.1 爆火前信号确实存在

从 Dify、RAGFlow、MCP 代表仓库来看，在真正大规模出圈前，往往会先出现：

- 连续数周的 star 增速抬升
- fork 同步增长
- 提交活跃
- issue / discussion 增加

### 8.2 不同项目类型，爆发模式不同

- 产品平台型：Dify、RAGFlow
  - 往往多轮增长，波段明显。
- 协议型：MCP、A2A
  - 主仓库不一定最能代表真实热度，生态更重要。
- 病毒型消费/Agent 产品：OpenClaw
  - 可能在极短时间内从几百 stars 爆到几万。

### 8.3 只看总 stars 会误判

真正有用的是：

- 增速
- 加速度
- 生态扩散
- 活跃度

而不是某个仓库当前有多少 stars。

## 9. 竞品与差异化机会

现有替代品：

- GitHub Trending
  - 只看短期热度，不适合长期监控和量化分析。
- Star History
  - 适合看历史曲线，但 2026 年后受 GitHub stargazers 限制影响很大。
- OSS Insight
  - 很强，但更偏分析平台，不是“私人监控器 + 预警器”。

你的工具可以差异化在：

- 自定义观察名单
- 每日自动采集
- 爆发预警分数
- 主题集合监控
- 面向中文用户的解释层和推荐层

## 10. 可行性结论

### 10.1 可行部分

- 从今天开始，基于 GitHub API 自建每日快照库：完全可行。
- 针对选定仓库做趋势曲线、排行榜、异常检测：可行。
- 对已有热门仓库做历史回填：可行，但需要依赖 OSS Insight 这类第三方数据源。

### 10.2 风险部分

- 不能再只靠 GitHub stargazers API 做任意公开仓库的完整历史回溯。
- 协议/生态项目无法被单仓库完整表示。
- 若观察名单过大，采集频率和 API 配额需要控制。

### 10.3 最终判断

这个 idea 是可行的，而且有明确价值。

更准确地说：

- 它不是一个“通用 GitHub 分析平台”
- 而是一个“面向 AI 开源趋势的轻量监控 + 量化预警工具”

这个定位更聚焦，也更容易做出 MVP。
