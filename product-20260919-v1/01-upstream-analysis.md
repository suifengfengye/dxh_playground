# 工作 1：ai-job-search 功能与依赖拆解

版本：v1 / 2026-09-19。性质：公开源码静态分析，不是运行测试或商业尽调。

## 1. 结论先行

ai-job-search 不是可以直接换皮上线的 SaaS 后端，而是「职业资料 + 提示词工作流 + 若干独立工具 + 本地文件状态」组成的个人求职工作区。Claude Code 提供了对话、工具调用、流程编排、上下文管理和文件操作能力。

产品化要继承的是求职方法与质量控制，不是让云端服务器替用户启动 Claude Code。仅把 CLI 包进容器，不能满足“去掉 Claude Code 运行时依赖”的目标。

核心用户价值：

1. 把分散经历组织成可复用的事实资料。
2. 判断一份职位是否值得投入申请时间。
3. 根据职位定制材料，检查事实、表达、排版与文本可解析性。
4. 保留每次申请上下文，支持跟进、面试和结果复盘。

## 2. 证据口径

- 仓库：[MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search)。
- 分析固定版本：`09435eb1a572eddbd0180e8ea9c3acf84f90604a`，来自当时 `HEAD`；默认分支 `master`。
- 2026-09-19 GitHub API 读取值：43,293 Stars、14,868 Forks；这是关注度快照，不是活跃用户数或付费用户数。
- README 作者自述：69 次定制申请、20 次初面、1 份签约。属于个人成功案例，未经独立核验，不能推导产品平均效果、因果关系或付费意愿。
- 已阅读 README、SETUP、核心命令阶段、评分规则、搜索接入说明、安全说明及 PDF 验证工具。文件树完整返回，未截断。
- 未运行 Claude Code、职位抓取、LLM 生成、PDF 编译或上游测试；未登录任何用户账户。
- 下文“已有”表示存在实现或工作流定义，不等于已验证生产可用。
- 频率均根据任务链推断，仓库没有提供可以验证的用户行为数据。

## 3. 实现层次

| 层 | 仓库内容 | 实际含义 |
|---|---|---|
| 用户入口 | `/setup`、`/apply` 等命令 | Markdown 提示词入口，不是 HTTP API |
| 业务规则 | 候选人、写作、评估、面试技能文件 | 由模型解释执行，部分包含人工确认 |
| 执行环境 | Claude Code 与其工具、reviewer 子代理 | 不是仓库自带的通用 Agent 服务 |
| 独立工具 | Bun/TypeScript 搜索 CLI；Python 验证、薪资、状态工具 | 部分可改造成受控服务 |
| 状态 | Markdown、CSV、JSON、本地文件夹 | 个人工作区，不具备多租户事务语义 |
| 文档 | LaTeX 模板、字体、PDF 检查 | 本地编译管线，不是在线编辑器 |

其他 Agent 可以使用 `.agents/skills` 下的搜索工具；README 也提及社区适配。这不表示完整工作流已经去除了 Claude Code 耦合。[S01][S02]

## 4. 全功能清单

类型：W = 提示词工作流；T = 独立工具；A = 模板/文件约定。频率指“求职活跃期内”的预期使用。

| ID | 功能 / 入口 | 输入 → 输出 | 实现与边界 | 预期频率 | 证据 |
|---|---|---|---|---|---|
| U01 | 资料初始化 `/setup` | 文档目录、单份 CV 或访谈 → 结构化资料 | W；三条路径、缺项追问、冲突确认、增量更新 | 首次必需，后续偶发 | S03 |
| U02 | 目标与约束配置 | 岗位、地点、语言、偏好 → 搜索与评估规则 | W/A；可按 section 更新，含行为与职业动机资料 | 首次必需，变化时更新 | S03、S05 |
| U03 | 经历扩充 `/expand` | 已提供的资料、公开作品链接、课程 → 能力证据 | W；推断与直接证据区分，用户确认后写入 | 低 | S06 |
| U04 | 多源职位发现 `/scrape` | 个人查询与门户 → 新职位集合 | W+T；门户发现、CLI 调用、WebSearch 降级 | 高，依赖主动搜索习惯 | S07 |
| U05 | 去重、有效性与源健康 | 职位 URL、历史、截止日期 → 新/重复/过期、健康报告 | W+T；识别批量发布，状态持久化，有限探测 | 搜索时自动 | S07、S08 |
| U06 | 内推联系人入口 | 公司、职位 → LinkedIn 搜索链接 | W；生成联系入口，不等于找到联系人或发送消息 | 中低 | S07 |
| U07 | 批量初筛 `/rank` | 已抓取职位 + 资料 → 分数、优势、缺口、短名单 | W+T；默认最多 10 个，初筛不做公司研究；与深度评估不同 | 搜索量大时高 | S08 |
| U08 | 单职位导入 `/apply` | URL 或粘贴全文 → 职位文本与元数据 | W；读取失败不从标题编造，检查来源主机 | 每次申请 | S04 |
| U09 | 岗位适配评估 | 职位 + 资料 → 条件判断、维度评分、建议 | W；先展示评估，再询问是否生成 | 每次申请 | S04、S05 |
| U10 | 公司研究 | 公司身份、公开信息 → 可核实事实与缓存 | W；reviewer 独立研究，最终事实再次确认，30 天缓存 | 生成/面试时 | S04、S05 |
| U11 | 定制 CV | 主资料 + 职位 + 模板 → CV 草稿 | W+A；根据相关性调整摘要、经历及用词，不以旧定制 CV 为事实源 | 每次重点申请 | S04、S09 |
| U12 | 定制求职信 | 职位 + 资料 + 写作风格 → Cover Letter | W+A；面向解决问题，不重复整份履历 | 视职位要求而定 | S04、S10 |
| U13 | 申请表回答 | 问题、字数限制、经历 → 可粘贴答案 | W；可选第三类产物，不自动填写外站表单 | 部分申请 | S11 |
| U14 | 起草与审阅分离 | 草稿 → 批评、事实审计、修订 | W；独立上下文 reviewer；仍不能保证消除幻觉 | 每次生成 | S04 |
| U15 | PDF 编译与版面检查 | 模板草稿 → PDF、检查结果、修订 | W+T+A；默认 CV 恰好 2 页、信恰好 1 页 | 每次导出 | S04、S09、S10、S12 |
| U16 | ATS 文本可解析性 | PDF + 职位要求 → 文本、联系方式、顺序与关键词检查 | W+T；pypdf 优先，pdftotext 后备；缺依赖可降级。不是 ATS 厂商评分 | 每次生成 | S04、S12 |
| U17 | 申请记录与档案 | 生成材料、职位 → CSV、职位及提交材料档案 | W/A；`drafted` 与 `applied` 分开；同公司同岗位路径可能碰撞 | 高频、自动伴随 | S04、S13 |
| U18 | 结果更新 `/outcome` | 用户反馈 → 阶段、日期、备注、结果 | W；面试、offer、拒绝、入职等，保留历史 | 每次进展 | S13 |
| U19 | 跟进与感谢信 | 无消息申请、提交档案 → 跟进草稿、感谢信 | W；默认 10 天无消息，最多两次跟进；只起草不发送 | 中 | S13 |
| U20 | 沉默申请清理 | 长期无消息记录 → 待确认的 no_response | W；默认 60 天，确认后批量更新，不自动认定拒绝 | 低 | S13 |
| U21 | 面试准备 `/interview` | 提交版本、阶段、反馈 → 研究、题目、STAR、模拟面试 | W；围绕雇主实际看过的材料，不虚构经历 | 到面试阶段才高 | S14 |
| U22 | Gmail 状态同步 | 邮箱信号 → 待批准变更与邮件来源 | W + 外部连接器；先批准再写状态，不把 offer 自动当入职 | 中高，需授权 | S15 |
| U23 | 报表 `/html-report` | Tracker 与历史 → 离线 HTML、图表、筛选表 | W；生成报告文件，不是长期在线服务 | 中 | S16 |
| U24 | Notion 同步 | 已排序职位和申请 → Notion 数据库 | W + MCP/OAuth；单向，文件名而非文件内容，不回写 | 中，限 Notion 用户 | S17 |
| U25 | 能力差距 `/upskill` | 单职位或申请/初筛记录 → 缺口热图与学习计划 | W；资源检索、优先级、时间估算 | 低 | S18 |
| U26 | 薪资参考 | 用户自带薪资数据 → 指数与基线比较 | T；Python 查询与 Excel 转换，无内置全球实时薪资库 | 低 | S19 |
| U27 | 模板扩展 `/add-template` | 自定义模板和编译命令 → 注册、测试编译、启用 | W；可支持 LaTeX、Typst 等工具链 | 低、技术用户 | S20 |
| U28 | 门户扩展 `/add-portal` | 门户 URL → 新 CLI 技能与实测 | W；生成代码，登录墙拒绝，限制条款警告 | 低、维护者 | S21 |
| U29 | 重置与框架维护 | 清理范围或上游更新 → 重置/差异报告 | W+T；重置输入 RESET；含 CI、版本检查、技能 lint | 低、维护者 | S01、S22 |

## 5. 三条关键链路

```text
资料建立：
文档 / 访谈 -> 提取事实 -> 冲突与缺项 -> 用户确认 -> 可复用资料

申请准备：
URL / 正文 -> 职位解析 -> 适配评估 -> 用户确认
-> 起草 -> 独立审阅 -> 修订 -> PDF / 文本检查 -> drafted
-> 用户自行到外站投递 -> 明确记录 applied

持续求职：
搜索 -> 去重 -> 初筛 -> 申请准备 -> 跟进 / 面试 -> 结果
-> 用真实结果辅助校准资料及后续策略
```

重要：`/apply` 名称容易令人误解。源码生成材料和记录草稿，不提供可靠的自动投递功能；浏览器自动填写、验证码处理、自动发送邮件也不是已核实的核心能力。

## 6. 评分方法及不能照搬的假设

上游加权项：技能 30%、经历 25%、行为/文化 15%、职业方向 30%；地点是门槛，不加权。分段：75+ Strong、60–74 Good、45–59 Moderate、30–44 Weak、低于 30 Poor。[S05]

这是一套模型执行的启发式规则，不是经过招聘结果校准的录用概率模型。特别需要调整：

- 美国 Resume 不应统一强制两页；建议首版允许 1 或 2 页，按内容选择。
- “没有填写某语言”不能直接当作“不掌握该语言”；应先补充确认。
- 安全许可、工作授权、签证赞助存在岗位与法律差异，不能照搬“多数国家”的硬拒绝判断。
- 缺少公司证据时，不输出貌似精确的文化匹配分。
- 上游有要求在 AI 工具经历中点名 Claude Code 的规则，属于上游定位，不能写入所有用户简历。
- 已提交材料不可被后续资料更新覆盖；新申请应有独立 ID，不能仅使用公司名和岗位名作唯一键。
- SECURITY 与 README/SETUP 对资料是否被 gitignore 的描述存在口径差异；不据此承诺“默认绝不泄露”。云端产品必须独立建立隐私边界。

## 7. 云端迁移依赖矩阵

| 上游依赖 | 用户承担的问题 | 云端产品替代方式 | 是否消失 |
|---|---|---|---|
| Claude Code 订阅/CLI | 安装、登录、命令、会话恢复 | 自有业务流程 + 服务端模型 API 适配层 | CLI 彻底移除；模型推理仍需要 |
| Claude 工具和 reviewer | 工具权限、上下文、循环不确定 | 固定流程、结构化输出、审阅阶段、步数/费用上限 | 需重新实现编排 |
| Git 与本地目录 | 克隆、更新、文件寻址、误公开 | 账户、数据库、私有对象存储、版本记录 | 从用户端消失 |
| Bun / Python | 安装、版本及库冲突 | 必要工具放在服务端；不要求保留所有旧 CLI | 运维依赖仍存在 |
| LaTeX / 字体 | 编译失败、字体与分页问题 | 受控渲染服务；实现阶段比较 HTML-to-PDF 与现有引擎 | 用户免安装，不是无渲染依赖 |
| pypdf / Poppler | 可选依赖导致质量检查降级 | 服务端固定验证链；失败不能伪装成功 | 纳入生产依赖 |
| 搜索门户 | 反爬、区域覆盖、条款 | MVP 只处理用户导入且允许读取的职位；正文始终可用 | 数据来源限制仍存在 |
| Gmail / Notion | 连接器和授权 | MVP 不接入 | 直接后置 |
| 本地可信单用户 | 文件隔离依赖使用习惯 | 身份鉴权、租户隔离、任务隔离、隐私控制 | 必须新增 |

“去掉环境依赖”准确含义：用户只需浏览器与网络，不安装工具、不配 API Key。平台仍需承担模型、解析、渲染、存储和运维成本。可使用 Claude 模型 API，但不能依赖 Claude Code CLI 或其会话订阅；模型供应商尚未选定。

## 8. 商业与合规边界

1. MIT 允许商业使用，但复用代码和实质性内容要保留版权与许可；字体、第三方模板、数据、品牌需逐项审查，MIT 不授予职位数据抓取权。[S22]
2. LinkedIn 搜索技能明确标注不用于商业或批量采集。MVP 不调用该 CLI，用户粘贴 LinkedIn URL 时改为提示粘贴职位正文。[S23]
3. freehire 文档说明无正式 SLA、偏技术岗位。后端开源不等于托管 API 可无限商用，数据授权与覆盖率需另外验证。[S24]
4. 上传简历涉及联系方式、经历和潜在敏感信息。云端不再具备本地文件留在用户机器的属性，应明确处理方、保存期限、删除路径与模型数据政策。
5. 禁止把生成量、Star 数、作者成功案例包装成“保证面试”“ATS 必过”或“自动拿 offer”。
6. 主要待验证假设：非技术用户愿否付费、生成材料比通用聊天模型省多少时间、重复使用频率、云端资料信任、单次生成毛利。

## 9. 固定版本来源索引

以下链接均锁定同一个版本。引用段落使用文件中的同名标题定位。

| 编号 | 来源 |
|---|---|
| S01 | [README：功能、案例、依赖、扩展](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/README.md) |
| S02 | [SETUP：安装与资料设置](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/SETUP.md) |
| S03 | [setup.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/setup.md) |
| S04 | [apply.md：Step 0–6b](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/apply.md) |
| S05 | [04-job-evaluation.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/skills/job-application-assistant/04-job-evaluation.md) |
| S06 | [expand.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/expand.md) |
| S07 | [job-scraper/SKILL.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/skills/job-scraper/SKILL.md) |
| S08 | [rank.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/rank.md) |
| S09 | [05-cv-templates.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/skills/job-application-assistant/05-cv-templates.md) |
| S10 | [06-cover-letter-templates.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/skills/job-application-assistant/06-cover-letter-templates.md) |
| S11 | [08-application-forms.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/skills/job-application-assistant/08-application-forms.md) |
| S12 | [tools/verify_pdf.py](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/tools/verify_pdf.py) |
| S13 | [outcome.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/outcome.md) |
| S14 | [interview.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/interview.md) |
| S15 | [gmail-sync.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/gmail-sync.md) |
| S16 | [html-report.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/html-report.md) |
| S17 | [notion-sync.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/notion-sync.md) |
| S18 | [upskill/SKILL.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/skills/upskill/SKILL.md) |
| S19 | [薪资工具说明](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/tools/README_SALARY_TOOL.md) |
| S20 | [add-template.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/add-template.md) |
| S21 | [add-portal.md](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.claude/commands/add-portal.md) |
| S22 | [LICENSE](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/LICENSE) / [SECURITY](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/SECURITY.md) |
| S23 | [LinkedIn 使用范围](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.agents/skills/linkedin-search/SKILL.md) |
| S24 | [freehire 范围与托管限制](https://github.com/MadsLorentzen/ai-job-search/blob/09435eb1a572eddbd0180e8ea9c3acf84f90604a/.agents/skills/freehire-search/SKILL.md) |
