# 自媒体内容工厂：一个 `CompositeBackend` 实战案例

命令行给一个主题，agent 写出 2 篇 dev.to 文章，**真的调用发布脚本发出去**。

它回答的是《langchain 中的常用 backend》没答的问题：**5 条路径怎么分工？**
答案是 `CompositeBackend`——按路径前缀把文件操作路由到不同后端，一个 agent 同时拥有
「真实磁盘 + 命令执行 + 长期记忆 + 临时草稿」四种能力。

## 目录结构

```
auto_post_agent/
├── agent.py              # 主角：CompositeBackend 装配 + 系统提示 + 命令行对话
├── workspace/            # default 后端的工作区（真实落盘 + 可执行）
│   └── publish.py        # 发布脚本，agent 用 execute 调用它
├── posts/                # 定稿区（/posts/）
└── archive/              # 归档区（/archive/）
```

## 挂载表：每条路径为什么是它

| 虚拟路径 | backend | 职责 | 换成别的会怎样 |
| --- | --- | --- | --- |
| `/` | `LocalShellBackend` | 工作区，`publish.py` 在这里，负责 **写文件 + 执行发布** | 换 `FilesystemBackend` 就连 `execute` 工具都没有，发不出去 |
| `/posts/` | `FilesystemBackend` | 定稿文案真实落盘 | 换 `StateBackend`：进程一退文案就没了，API 挂了也没法手动发 |
| `/archive/` | `FilesystemBackend` | 已发布快照，带发布结果，可回溯 | 混在 `/posts/` 里会被下一轮同名 slug 覆盖 |
| `/memory/` | `StoreBackend` | 账号人设 + 发布台账 | 换 `StateBackend`：换 thread 就失忆，会重复选题、重复发 |
| `/draft/` | `StateBackend` | 选题脑暴与淘汰 | 落到磁盘会污染交付仓库 |

### 关键坑 1：`execute` 不参与路由

```python
CompositeBackend(
    default=LocalShellBackend(root_dir=WORKSPACE, inherit_env=True),  # ← 这里不能是 State
    routes={
        "/memory/": StoreBackend(namespace=lambda _rt: ("auto_post", "editor")),
        "/posts/": FilesystemBackend(root_dir=POSTS),
        "/archive/": FilesystemBackend(root_dir=ARCHIVE),
        "/draft/": StateBackend(),
    },
)
```

- 文件操作（`ls`/`read_file`/`write_file`/`edit_file`/`glob`/`grep`）**按前缀路由**，最长前缀优先。
- 但 `execute` **永远走 `default`**，`routes` 里挂什么后端都不影响它。
- `execute` 工具**是否注册**，只看 `default` 是否实现了 `SandboxBackendProtocol`。

一行代码验证：

```python
from deepagents.middleware.filesystem import supports_execution

supports_execution(CompositeBackend(default=LocalShellBackend(root_dir="workspace"), routes=routes))  # True
supports_execution(CompositeBackend(default=StateBackend(), routes=routes))                          # False
```

**想让 agent 既能路由又能跑命令，`default` 只能是 `LocalShellBackend`。**

### 关键坑 2：`virtual_mode` 不约束 shell

`LocalShellBackend(virtual_mode=True)` 只把**文件类工具**锁在 `root_dir` 内。
`execute` 里的 `cd ../.. && rm -rf` 它一概不管——所以本次专门在系统提示里要求
「归档必须用 `write_file`，不许用 `cp`」：

- 用 `write_file` 写 `/archive/x.md` → 走路由，落到归档区，职责清晰；
- 用 `execute cp ../posts/x.md ../archive/x.md` → 走 shell，**绕过整个挂载表**，
  磁盘上结果一样，但路由就形同虚设了。

这不是洁癖。第一次真跑时 agent 就是用 `cp` 归档的，`/archive/` 那条路由全程没被调用。

### 关键坑 3：`namespace` 别抄成 `thread_id`

`StoreBackend` 的 namespace 工厂签名是 `Callable[[Runtime], tuple[str, ...]]`。
把 `thread_id` 塞进去，等于**把 `StoreBackend` 用成了 `StateBackend`**——换 thread 就失忆，
跨会话记忆这个最值钱的特性直接浪费。

这里用固定 namespace，最简单也最稳：

```python
"/memory/": StoreBackend(namespace=lambda _rt: ("auto_post", "editor")),
```

> 注意：工厂里读 `rt.context.user_id` 是有前提的——你必须给 `create_deep_agent` 传
> `context_schema` 并在每次调用时带上 `context=`，否则 Runtime 供不上，源码会直接抛
> `RuntimeError`（不会静默降级）。单用户 demo 用固定 namespace 就够；要多租户，
> 就加 `context_schema`，再把它改成 `lambda rt: ("auto_post", rt.context.user_id)`。

### 关键坑 4：`urllib` 的默认 User-Agent 会被 dev.to 挡在门外（403）

`publish.py` 一开始没设 `User-Agent`，`urllib` 就填了默认的 `Python-urllib/3.12`，
真发时报 **403**。这个 403 极具误导性：**没有响应体、没有 `content-type`、
`server: Varnish`**——请求根本没到 API，是边缘层按 UA 拉黑拦掉的。

实测对照（同一个 key，只换 UA）：

| User-Agent | `GET /api/users/me` |
| --- | --- |
| `Python-urllib/3.12` | **403**（空 body） |
| `auto-post-agent/1.0` | 200 |
| `curl/8.7.1` | 200 |
| `python-requests/2.32.3` | 200 |

既不是 key 失效，也不是 dev.to 不开放——换个 UA 就通。所以脚本里显式带上：

```python
USER_AGENT = "auto-post-agent/1.0"
```

并加了一条防御：**403 且响应体为空时，直接告诉你这是 UA 被拦**，别再让人回头怀疑 key。

### 关键坑 5：连发多篇必然撞上 429 限流

4 篇一起发，前 2 篇 `201`，后 2 篇立刻变成：

```json
{"error":"Rate limit reached, try again in 30 seconds","status":429}
```

**这里真正危险的不是限流本身，而是 `exit 2` 的语义**：如果 agent 把「API 报错」
理解成「文案有问题」，它就会去乱改本来已经合规的文案。所以退出码语义必须分清：

| 退出码 | 含义 | agent 该做什么 |
| --- | --- | --- |
| `0` | 发布成功 | 归档、记台账 |
| `1` | 文案不合规 | **改文案**，重跑 |
| `2` | API 层问题 | **别动文案**，看 `hint`，原样重跑 |

`publish.py` 对 429 会自动等待（从响应体里解析 `try again in N seconds`）并重试，
同时在输出里附上 `hint: "429 是平台限流，文案本身没问题，不要改文案"`。

顺带一个 API 边界：**dev.to 没有删除文章的端点**，`DELETE /api/articles/:id` 返回 404 HTML；
articles 端点只有 GET / POST / PUT。发错了只能去 dev.to 后台删。

## 环境

```text
python 3.12 / deepagents 0.7.21 / langgraph / langchain
环境变量 DEEPSEEK_API_KEY
可选环境变量 DEVTO_API_KEY（dev.to 后台 Settings → Extensions → API Keys）
```

## 快速开始

```bash
python agent.py
主题> 用大白话讲清楚 Python 的 asyncio 到底是什么
```

不设 `DEVTO_API_KEY` 时 `publish.py` 自动走 **dry-run**：只做本地合规校验，不真的发到外网。
`/posts/`、`/archive/`、`/memory/` 里该有的产物一个不少，演示完全够用。

想真发：

```bash
export DEVTO_API_KEY=xxxxxxxx
python agent.py
```

## 三个可复现的对照实验

**实验 1（记忆跨 thread）**——`/memory/` 的 `StoreBackend` 是不是真的跨会话：

```bash
python agent.py
主题> 用大白话讲清楚 Python 的 asyncio 到底是什么
主题> :new                      # 换一个全新的 thread
主题> 先别写新文章，只回答我：你记得我们的账号人设吗？我们之前发过哪些选题？
```

第二个 thread 能直接背出人设和发布台账 = 记忆存在 `StoreBackend` 里，而不是 `StateBackend`。
（实测日志里它连「已淘汰的选题」都记得。）

> `InMemoryStore` 只活在进程内，所以这个实验要在**同一个进程**里用 `:new` 做。
> 想跨进程持久化，把 store 换成 Redis / Postgres 实现即可，`StoreBackend` 的代码不用改。

**实验 2（执行权）**：把 `default` 改成 `StateBackend()` 重新启动，让它"发一下文章"——
它会连 `execute` 工具都找不到。用代码验证见上面的 `supports_execution`。

**实验 3（合规自检闭环）**：把 `posts/` 里某篇的 `tags` 改成中文（比如 `tags: 人工智能`），
再让它"发布这一篇"。`publish.py` 退出码 1 并打印：

```json
{"ok": false, "exit": 1, "step": "validate",
 "errors": ["非法 tag：'人工智能'，只允许小写字母/数字且不超过 30 字符（中文标签 dev.to 不接受）"]}
```

agent 会自己改 tag、重跑，直到退出码 0。**这就是 `execute` 的价值**——
把"验收标准"交给一个可判定的退出码，比让模型自我评价可靠得多。

## 一次真实运行的调用链

```text
  ● ls(/memory/)                          ⎿  No files found
  ● ls(/)                                 ⎿  ['/archive/', '/draft/', '/memory/', '/posts/', '/publish.py']
  ● write_file(/memory/persona.md, content: 29 行)
  ● write_file(/draft/brainstorm.md, content: 33 行)          ← 只在 state 里，磁盘上查无此物
  ● write_file(/posts/asyncio-plain-mental-model.md, ...)
  ● write_file(/posts/asyncio-pitfalls-and-fixes.md, ...)
  ● execute(python3 publish.py --file asyncio-plain-mental-model.md)
                                          ⎿  { "ok": true, "exit": 0, "dry_run": true, ... }
  ● write_file(/archive/asyncio-plain-mental-model.md, content: 201 行)   ← 走路由归档
  ● write_file(/memory/published.md, content: 15 行)
  ● ls(/archive/)                         ⎿  ['/archive/asyncio-...']
```

注意第一行 `ls(/)`：返回的 5 个名字里，`/archive/`、`/draft/`、`/memory/`、`/posts/`
**在磁盘上都不存在于 `workspace/` 下**，它们只是 `CompositeBackend` 把路由挂载点
叠加到 default 目录列表上的结果。只有 `publish.py` 是真的。

跑完之后：

```bash
$ find posts archive workspace -type f
archive/asyncio-pitfalls-and-fixes.md     # 归档区：发布结果 + 正文快照
archive/asyncio-plain-mental-model.md
posts/asyncio-pitfalls-and-fixes.md       # 定稿区：纯文案，可直接复制手动发
posts/asyncio-plain-mental-model.md
workspace/publish.py                      # 工作区：只有工具，没有产物
```

`/draft/` 的脑暴稿一个都没落盘，`workspace/` 干干净净。
