# 📇 Card #02 — Runnable 协议与 LCEL 管道

> **发布日期**：Day 2
> **预计阅读**：5 分钟（含代码）
> **🔁 今日复习**：Card #01（三层技术栈 + 为什么 ChatOpenAI 能接 DeepSeek）

---

## 🧠 一句话心法（背这句就够）

> **LangChain 里所有东西都是 `Runnable`；用 `|` 把它们串起来，就是 LCEL。**

---

## 🖼️ 心智锚

```
        输入
         │
         ▼
   ┌───────────┐
   │  Prompt   │  ← Runnable①
   └─────┬─────┘
         │  (自动传递)
         ▼
   ┌───────────┐
   │    LLM    │  ← Runnable②
   └─────┬─────┘
         │
         ▼
   ┌───────────┐
   │  Parser   │  ← Runnable③
   └─────┬─────┘
         │
         ▼
        输出

   chain = prompt | llm | parser
                ▲       ▲
              就是 Unix 的管道符 |
```

---

## 🔑 5 个关键点（组块 ≤ 7）

### 1. `Runnable` 是什么？
一个**统一接口**。LangChain 里的 LLM、Prompt、Parser、Retriever、Tool、甚至你自己写的普通函数——**全都是 Runnable**。

### 2. 每个 Runnable 都有 4 个"标准动作"（昨天的伏笔在这）

| 方法 | 干嘛的 | 什么时候用 |
|---|---|---|
| **`invoke(x)`** | 同步单次调用 | 大多数场景 |
| **`stream(x)`** | 流式返回 | 前端要打字机效果 |
| **`batch([x1,x2])`** | 批量并发 | 一次处理 100 条 JD |
| **`ainvoke(x)`** | 异步版 | FastAPI / async 环境 |

**"a" 开头 = async 版**。所以其实是 4 组 8 个方法：`invoke/ainvoke`、`stream/astream`、`batch/abatch`、`stream_events/astream_events`。

### 3. LCEL = LangChain Expression Language
就是 **用 `|` 把 Runnable 串起来**。灵感直接来自 Unix `cat file | grep xxx | wc -l`。

```python
chain = prompt | llm | parser
# 等价于把三个 Runnable 组合成一个新的 Runnable（也有 invoke/stream/batch）
```

### 4. 组合出来的 chain **还是 Runnable**
所以你可以套娃：

```python
big_chain = chain1 | chain2 | some_function
```

### 5. 为什么这个设计牛？
- **免费拿到 streaming**：chain 自动有 `.stream()`，不用手写
- **免费拿到 batch 并发**：`.batch([...])` 自动并行
- **免费拿到 async**：直接 `.ainvoke()` 就能塞进 FastAPI
- **免费拿到 LangSmith 追踪**：每一节都自动被追踪

**⭐ 一次抽象换来 4 大能力**——这就是为什么 LangChain 从 0.1 演化到今天，`Runnable` 是留下来的核心。

---

## 💻 最小可运行代码（今晚要跑的）

```python
# src/lcel_pipeline.py
"""Card #02 · LCEL 管道初体验"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0.3,
)

# 1️⃣ Prompt：一个 Runnable
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是招聘信息分析师，用一句话总结这份工作。"),
    ("human", "{jd}"),
])

# 2️⃣ Parser：一个 Runnable（把 AIMessage 提取成纯字符串）
parser = StrOutputParser()

# 3️⃣ 用 | 串起来 —— 这就是 LCEL
chain = prompt | llm | parser

# ─── invoke：单次调用 ───
jd_1 = "Senior Python Engineer, fully remote, FastAPI+Postgres."
print("【invoke】", chain.invoke({"jd": jd_1}))

# ─── stream：流式打字机效果 ───
print("\n【stream】", end="")
for chunk in chain.stream({"jd": jd_1}):
    print(chunk, end="", flush=True)
print()

# ─── batch：一次处理多条，自动并发 ───
jds = [
    {"jd": "React Frontend, hybrid Shanghai, 3+ yrs."},
    {"jd": "ML Engineer, PyTorch, on-site Beijing."},
    {"jd": "DevOps SRE, remote APAC, K8s+Terraform."},
]
print("\n【batch】", chain.batch(jds))
```

**运行**：
```bash
uv run python src/lcel_pipeline.py
```

**预期观察**：
- `invoke` 一次出结果
- `stream` 逐字符/逐词吐出（体验一下"打字机"）
- `batch` 3 条 JD 几乎**同时**出结果（不是串行 3 次！）

---

## ⚠️ 易混点 / 常见坑

### 坑 1：`|` 不是 Python 位或运算
LangChain **重载了** `Runnable.__or__`，所以只有当左边是 Runnable 时，`|` 才是"管道"。
以下都**不能**用 `|`：

```python
chain = "hello" | llm         # ❌ 字符串没有 __or__
chain = lambda x: x | llm     # ❌ 普通函数没有
```

要让普通函数进管道，用 `RunnableLambda`：

```python
from langchain_core.runnables import RunnableLambda
chain = RunnableLambda(lambda x: x.upper()) | llm
```

### 坑 2：Prompt 输入是 **dict**，不是字符串

```python
chain.invoke("hello")            # ❌ 报错：expected dict
chain.invoke({"jd": "hello"})    # ✅ 因为 prompt 里写了 {jd}
```

### 坑 3：不要再用旧写法
```python
# ❌ 旧世界（0.1/0.2）——已废弃
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
chain.run(jd="...")

# ✅ 新世界（0.3+）
chain = prompt | llm | parser
chain.invoke({"jd": "..."})
```

看到网上教程还在 `LLMChain` / `.run()` / `.predict()` —— **关掉页面**。

---

## 🎴 空白挑战（白天默想）

1. 用一句话解释：为什么说"LangChain 里所有东西都是 Runnable"很重要？
2. 一个 Runnable 有哪 4 个标准方法？分别什么时候用？
3. `chain = prompt | llm | parser` 中，`|` 到底是什么？为啥能用？
4. `chain.invoke("hello")` 报错了，最可能的原因？
5. 有 100 条 JD 要处理，用 `invoke` 循环 vs `batch`，差别在哪？

---

## 🛠️ 今晚练习（30 分钟）

- [ ] **10 分钟** — 跑通上面的 `lcel_pipeline.py`，亲眼看到 stream 和 batch 的差异
- [ ] **15 分钟** — **改造 Card #01 的 `hello_llm.py`**：
  - 把原来的 "直接调 `llm.invoke([HumanMessage(...)])`" 改成 LCEL 管道
  - 让它能通过 `.stream()` 流式输出"这份工作是否远程"的判断理由（不是单个字，让它讲两句话）
- [ ] **5 分钟** — commit：`git commit -m "day2: LCEL pipeline & streaming"`

---

## 🎁 Bonus：LCEL 的隐藏彩蛋（有时间再看）

**并行分支**：一个输入同时喂给多个 chain：

```python
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel(
    summary=summary_chain,
    is_remote=remote_chain,
    tech_stack=tech_chain,
)
result = parallel.invoke({"jd": "..."})
# result = {"summary": "...", "is_remote": "是", "tech_stack": [...]}
```

**这个能力在 JobLens 里超关键**：一份 JD 一次调用，同时抽出"标题/是否远程/技术栈/薪资"——比串行快 3–4 倍。Week 2 会大量用到。

---

## 🔮 明天预告 · Card #03

**主题**：`ChatPromptTemplate` 深入 + Message 类型全家桶（System / Human / AI / Tool）。

**今晚请留意**：你在 `ChatPromptTemplate.from_messages([...])` 里写的 `("system", "...")` 和 `("human", "{jd}")` —— 这些 tuple 明天会告诉你它们**其实是 Message 对象的语法糖**。

---

<details>
<summary>👀 空白挑战答案</summary>

1. 因为**统一接口**意味着**统一能力**：所有 Runnable 都免费拿到 `invoke/stream/batch/ainvoke` + LangSmith 追踪 + LCEL 组合能力。你学一次，处处能用。

2. **`invoke`** = 同步单次；**`stream`** = 流式打字机；**`batch`** = 批量并发（不是串行！）；**`ainvoke`** = 异步版（FastAPI 场景）。加 "a" 前缀就是 async 版。

3. `|` 是 LangChain 重载的 `Runnable.__or__` 运算符，把左右两个 Runnable 组合成一个**新的 Runnable**，前者输出自动成为后者输入。灵感来自 Unix 管道。

4. Prompt 期待的是 **dict**（因为模板里有 `{jd}` 这样的占位符）。要传 `{"jd": "hello"}`。

5. `invoke` 循环 = 串行 100 次网络请求（100 × 单次耗时）；`batch` = 并发发出（默认并发度 5–10，可调），总耗时 ≈ 单次耗时 × 100/并发度。**处理 100 条 JD 时 batch 快一个数量级**。

</details>

---

## 📌 30 秒复习卡（睡前对空气讲）

- **Runnable 是什么** → 统一接口
- **4 个方法** → invoke / stream / batch / ainvoke
- **LCEL 是什么** → `|` 串 Runnable
- **`ChatOpenAI` 为啥能接 DeepSeek**（复习昨天）→ OpenAI 兼容协议客户端

讲不下去的那一条，就是明早要复看的那一条。
