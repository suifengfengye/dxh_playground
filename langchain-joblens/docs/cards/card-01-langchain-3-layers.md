# 📇 Card #01 — LangChain 是什么 & 三层技术栈

> **发布日期**：Day 1
> **预计阅读**：3–5 分钟
> **🔁 今日复习**：（第一天，无）

---

## 🧠 一句话心法（背这句就够）

> **LangChain 给积木，LangGraph 给引擎，我们用它俩拼出会思考的应用。**

---

## 🖼️ 心智锚（这张图 30 天都用得上）

```
   ┌───────────────────────────────────────┐
   │   你的 App（JobLens）                 │
   ├───────────────────────────────────────┤
   │   LangGraph  → 有状态的"流程引擎"     │  跑长任务、流式、HITL
   ├───────────────────────────────────────┤
   │   LangChain  → 无状态的"积木"         │  Model/Tool/Prompt/Retriever
   ├───────────────────────────────────────┤
   │   LLM Providers (DeepSeek/OpenAI..)   │
   └───────────────────────────────────────┘
```

---

## 🔑 3 个关键点（组块）

1. **LangChain = 抽象层**
   把不同厂商的 LLM、向量库、工具**统一成一个接口**，核心协议是 `Runnable`（明天讲）。

2. **LangGraph = 运行时**
   当流程不再是一条直线（要循环、分支、暂停、恢复），就升级到它。

3. **判断标准**
   - 一条链走完 → **LangChain**
   - 需要 agent 循环 / 多步骤状态 → **LangGraph**

---

## 💻 最小可运行代码（DeepSeek 版）

```python
# src/hello_llm.py
"""Card #01 · JobLens Day 1"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",   # ← 关键：换 base_url 就能用 DeepSeek
    temperature=0.3,
)

jd = """
We are hiring a Senior Python Backend Engineer.
Location: fully remote (anywhere in APAC timezone).
Stack: FastAPI, Postgres, Kafka.
"""

resp = llm.invoke([
    SystemMessage(content="你是一个招聘信息分析助手，只回答 是 / 否 / 未提及。"),
    HumanMessage(content=f"这份工作是否支持远程？\n\n{jd}"),
])
print(resp.content)
```

**运行前**：
```bash
uv add langchain langchain-openai python-dotenv
echo "DEEPSEEK_API_KEY=sk-xxx" > .env
echo ".env" >> .gitignore
```

**运行**：
```bash
uv run python src/hello_llm.py
# 预期输出：是
```

---

## 🎁 元知识：为什么 `ChatOpenAI` 能接 DeepSeek？

> **`ChatOpenAI` ≠ 只能用 OpenAI。它是 "OpenAI 兼容协议客户端"。**
> 所有走 OpenAI 兼容接口的服务都能用它接入 —— 只改 `base_url`。

| 服务 | model | base_url |
|---|---|---|
| **DeepSeek** | `deepseek-chat` / `deepseek-reasoner` | `https://api.deepseek.com/v1` |
| Moonshot | `moonshot-v1-8k` | `https://api.moonshot.cn/v1` |
| 智谱 GLM | `glm-4` | `https://open.bigmodel.cn/api/paas/v4` |
| SiliconFlow | 多种 | `https://api.siliconflow.cn/v1` |
| Ollama（本地）| `llama3.1` | `http://localhost:11434/v1` |

**换模型 = 改环境变量，不用改代码。** 这是 LangChain 送你的第一个红利。

---

## ⚠️ 易混点 / 常见坑

1. ❌ "LangChain 就是 Agent 框架"
   → 错。LangChain **不是** agent 框架，它只是积木；`create_agent` 只是官方用积木拼好的成品。

2. ❌ 还在用 0.1/0.2 时代的 `LLMChain` / `initialize_agent`
   → **已废弃**。**2025 年后统一用 LCEL（`prompt | llm | parser`）+ `create_agent`**。
   你如果看到网上教程还在写 `LLMChain(llm=llm, prompt=prompt)`，**关掉那个页面**。

3. ⚠️ **DeepSeek `reasoner` 不支持 tool calling**
   → 学到 Agent / Tool 那节必须切回 `deepseek-chat`。
   记忆口诀：**"reasoner 只会想，chat 才会用工具"**。

---

## 🎴 空白挑战（白天默想，答案在最下方）

1. LangChain / LangGraph / LLM Provider 三层，各自负责什么？（不看图说）
2. 什么信号出现时，我就该从 LangChain 升到 LangGraph？
3. `LLMChain` 现在还能用吗？替代品是什么？
4. `ChatOpenAI` 明明叫这个名字，为什么能接 DeepSeek？换成 Moonshot 我该改什么？
5. DeepSeek 的 `chat` 和 `reasoner` 什么时候各自使用？

---

## 🛠️ 今晚练习（25 分钟）

- [ ] **5 分钟** — 去 https://platform.deepseek.com 注册 & 拿 API Key（充 10 块钱够学一个月）
- [ ] **5 分钟** — `cd langchain-joblens && uv init && uv add langchain langchain-openai python-dotenv`
- [ ] **5 分钟** — 建 `.env` 写 key；`.gitignore` 加 `.env`
- [ ] **5 分钟** — **手敲**（别复制）上面的 `hello_llm.py`
- [ ] **3 分钟** — `git init && git commit -m "day1: hello deepseek via langchain"` 推 GitHub
- [ ] **2 分钟** — 睡前闭眼 60 秒讲一遍今天的三层图

---

## 🔮 明天预告 · Card #02

**主题**：`Runnable` 协议与 LCEL 管道 —— LangChain 的灵魂。

**今晚请留意**：你调用的 `llm.invoke(...)` 这个方法名 —— **`invoke` / `stream` / `batch` / `ainvoke`** —— 明天你会发现 LangChain 里**几乎所有对象都有这四个方法**。这不是巧合。留个心眼。

---

<details>
<summary>👀 空白挑战答案（晚上练习时再翻）</summary>

1. **LangChain** = 无状态积木（统一 LLM/Tool/Prompt 接口）；**LangGraph** = 有状态引擎（循环/分支/HITL/流式）；**Provider** = 真正的模型服务。
2. 需要**循环、分支、中断/恢复、并行子任务、跨轮状态**——任何一个出现就升级。
3. 已废弃。用 **LCEL**（`prompt | llm | parser`）替代简单链，用 **`create_agent`** 替代 `initialize_agent`。
4. 因为 `ChatOpenAI` 本质是 **OpenAI 兼容协议客户端**，不绑定 OpenAI 公司。换 Moonshot 改 3 处：`model="moonshot-v1-8k"`、`api_key=os.getenv("MOONSHOT_API_KEY")`、`base_url="https://api.moonshot.cn/v1"`。
5. **`deepseek-chat`**：日常抽取、结构化、Function Calling —— 默认用它。**`deepseek-reasoner`**：复杂推理、匹配打分等需要动脑的场景；**不支持 tool calling**，Agent 场景不能用。

</details>
