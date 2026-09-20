# 🎯 LangChain · JobLens 学习计划

> 一个"边学 LangChain 边做个人作品"的 30 天计划。
> 目标：产出一个比 [ai-job-search](https://github.com/) 更易用的开源版求职助手 —— **JobLens**。

---

## 📚 学习方法

- **白天碎片时间**：打开对应 `docs/cards/card-NN-*.md`，3–5 分钟看一张卡
- **晚上到家**：完成卡片底部的「🛠️ 今晚练习」，代码写进 `src/`
- **睡前 60 秒**：闭眼对空气讲一遍今天的心法（费曼法）
- **周末**：把本周 5 张卡的能力"缝合"进 JobLens，push 一次 commit

---

## 🗓️ 30 天路线

| 周 | 主题 | 项目里对应的能力 |
|---|---|---|
| **Week 1** | LangChain 核心积木：Model / Message / Tool / **Runnable & LCEL** | 输入岗位 URL → LLM 抽结构化 JSON |
| **Week 2** | Prompt / Structured Output / Retriever / VectorStore | 岗位入库 + 语义搜索 |
| **Week 3** | Agents（`create_agent`）+ Tools + Memory | 自然语言查询岗位 |
| **Week 4** | LangGraph 基础 + Streaming + HITL + LangSmith 可观测 | 多步爬取/清洗/打分 + 前端流式 + 线上可观测 |
| **加餐** | Deep Agents（可选） | 让 agent 自主运营求职看板 |

---

## 📇 卡片索引（每完成一张就打勾）

### Week 1 · 核心积木

- [ ] [Card #01 — LangChain 是什么 & 三层技术栈](./docs/cards/card-01-langchain-3-layers.md)
- [ ] [Card #02 — Runnable 协议与 LCEL 管道](./docs/cards/card-02-runnable-lcel.md)
- [ ] Card #03 — Prompt Template 与 Message 类型（待发布）
- [ ] Card #04 — Structured Output（结构化输出）（待发布）
- [ ] Card #05 — 周末缝合：从 JD 抽结构化岗位信息（待发布）

### Week 2 · 数据与检索
- [ ] Card #06 – #10（待发布）

### Week 3 · Agent
- [ ] Card #11 – #15（待发布）

### Week 4 · LangGraph & 上线
- [ ] Card #16 – #20（待发布）

---

## 🧠 复习节奏（SM-2 间隔重复）

每张新卡学完后，按以下节奏复习：
- **Day +1**：快速回忆心法 + 空白挑战（1 分钟）
- **Day +4**：默写关键代码（3 分钟）
- **Day +7**：口头讲给自己听（1 分钟）
- **Day +15**：结合项目使用（融入 JobLens）

我会在每张新卡的开头写「🔁 今日复习」，提醒你复习哪几张旧卡。

---

## 🛠️ 项目：JobLens

> 一个能"看懂"招聘信息、按你偏好智能筛选、给出匹配理由的求职助手。

### 技术栈
- **语言**：Python 3.11+
- **包管理**：uv
- **LLM**：DeepSeek（`deepseek-chat` 通用，`deepseek-reasoner` 只做推理打分）
- **框架**：LangChain + LangGraph（后期）
- **可观测**：LangSmith

### 路线图
- [ ] MVP：粘贴 JD → 输出结构化 JSON（Week 1 结束）
- [ ] V0.2：批量爬取 + 向量搜索（Week 2）
- [ ] V0.3：自然语言查询 Agent（Week 3）
- [ ] V0.4：多步工作流 + 流式前端（Week 4）
- [ ] V1.0：部署上线，开源

---

## 📊 进度追踪

- 开始日期：2026-09-09
- 今日：Day 0（环境准备中）
- 已完成卡片：0 / 30
