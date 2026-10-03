"""实战案例：自媒体内容工厂（auto-post-agent）。

命令行给一个主题，agent 写出 1 篇 dev.to 文章并真的发布出去。
一个 agent 用 5 条路径分工，靠 CompositeBackend 拼起来：

    /            -> LocalShellBackend   工作区：publish.py 在这里，负责写文件 + 执行发布
    /posts/      -> FilesystemBackend   定稿文案真实落盘（API 挂了也能直接拿去手动发）
    /archive/    -> FilesystemBackend   已发布快照，可回溯对比
    /memory/     -> StoreBackend        长期记忆：账号人设 + 发布台账，换会话也记得
    /draft/      -> StateBackend        短期：选题脑暴与淘汰，进程退出即消失

【关键坑】CompositeBackend 的 execute 不参与路由，它永远走 default；
而且 execute 工具是否注册，只取决于 default 是否是 SandboxBackendProtocol。
所以 default 必须是 LocalShellBackend，否则 agent 连发布工具都看不到。

用法：
    export DEVTO_API_KEY=xxx      # 不设置则走 dry-run：只做本地合规校验
    python agent.py               # 命令行对话，输入主题
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import (
    CompositeBackend,
    FilesystemBackend,
    LocalShellBackend,
    StateBackend,
    StoreBackend,
)
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

# --------------------------------------------------------------------------
# 1. 目录与依赖
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR / "workspace"  # default 后端的工作区
POSTS_DIR = BASE_DIR / "posts"  # 定稿区
ARCHIVE_DIR = BASE_DIR / "archive"  # 归档区

for _d in (WORKSPACE_DIR, POSTS_DIR, ARCHIVE_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# 【⚠️注意】这里依赖环境变量中已经配置了 DEEPSEEK_API_KEY
llm = init_chat_model("deepseek-v4-flash")
store = InMemoryStore()  # 想跨进程保留记忆，换成 Redis / Postgres 版 store 即可


def build_agent():
    """装配 CompositeBackend：一个 default + 四条路由。"""
    backend = CompositeBackend(
        # default 必须是有 execute 能力的后端，否则 execute 工具不会注册
        default=LocalShellBackend(
            root_dir=WORKSPACE_DIR,
            virtual_mode=True,  # 文件操作锁在 workspace 内（注意：不约束 shell 命令）
            inherit_env=True,  # 继承 PATH，python3 才找得到
            timeout=60,
        ),
        routes={
            # namespace 故意不写 thread_id -> 换 thread、换会话都还读得到
            "/memory/": StoreBackend(namespace=lambda _rt: ("auto_post", "editor")),
            "/posts/": FilesystemBackend(root_dir=POSTS_DIR, virtual_mode=True),
            "/archive/": FilesystemBackend(root_dir=ARCHIVE_DIR, virtual_mode=True),
            "/draft/": StateBackend(),
        },
    )

    return create_deep_agent(
        model=llm,
        tools=[],
        backend=backend,
        checkpointer=InMemorySaver(),  # 让 /draft/ 在同一个 thread 内可读写
        store=store,
        system_prompt=SYSTEM_PROMPT,
    )


SYSTEM_PROMPT = """你是「自媒体内容工厂」的主编。用户给你一个主题，你要产出 **1 篇**面向 dev.to 的技术文章，并且真的发布出去。

你的路径是一张虚拟挂载表，五块区域职责固定：

| 路径 | 用途 | 说明 |
| --- | --- | --- |
| `/` | 工作区 | `publish.py` 发布脚本就在这里，用 execute 调用它 |
| `/posts/` | 定稿区 | 1 篇定稿文案，会真实落盘 |
| `/archive/` | 归档区 | 已发布版本的快照，带发布结果，可回溯 |
| `/memory/` | 长期记忆 | 账号人设 + 已发布台账，跨会话保留 |
| `/draft/` | 临时草稿 | 选题脑暴与淘汰，进程退出即消失，别放交付物 |

每篇文章 = YAML front matter + markdown 正文：

    ---
    title: 标题
    tags: ai, agent, python
    ---

    正文……

工作流（按顺序做）：

1. 开工前先 `ls /memory/` 并读里面的人设与台账，避免重复选题；如果是空的就自己建。
2. 在 `/draft/` 里脑暴 3 个选题，淘汰 1 个，说明淘汰理由，再动手写。
3. 1 篇定稿分别写到 `/posts/<英文短横线 slug>.md`。
4. 写完必须自检：`execute` 运行 `python3 publish.py --file <slug>.md`，按退出码分情况处理：
   - `exit 1` = 文案不合规，读 `errors` 改文案，再重跑；
   - `exit 2` = API 层问题，看 `hint`，**文案本身没问题，不要改文案**，等一会儿原样重跑
     （dev.to 连发多篇必然触发 429 限流，脚本已自动等待重试一次）。
   直到退出码为 0。**不要绕过脚本直接发**。

硬性规则：

- 正文语言跟随用户给的主题：中文主题就写中文文章，英文主题就写英文。
- `title` ≤ 128 字；`tags` 最多 4 个，**只能用小写字母和数字**（中文标签 dev.to 会拒绝，
  这是最常踩的坑，中文文章也必须用英文 tag）。正文写成成篇的技术文章，
  不要写成一两百字的短文。
- 发布通过后：用 `write_file` 把「发布结果（url、时间）+ 完整正文」写到 `/archive/<slug>.md`。
  **必须用 `write_file` 走归档路由**，不许用 `cp` / `mv` 之类的 shell 命令去复制：
  shell 永远走 default 后端，会绕过虚拟挂载表直接落到磁盘，那样归档就不受路由管理了。
- 把本次选题记进 `/memory/published.md`（追加一行：日期 / 主题 / slug / 状态）。
- `/memory/persona.md` 存账号人设（语气、读者、禁忌），第一次开工时建立。
- 绝对不要修改 `publish.py`，它是工具。
- 不要编造发布结果，一切以 `publish.py` 的 stdout 为准。没配 `DEVTO_API_KEY` 时它是
  dry-run，`url` 里会写明「没有真的发布」，照实汇报即可。

回复要求：先说清这 1 篇分别是什么角度，再贴 `publish.py` 给出的结果，最后一行给出
`/posts/` 里的文件名。不要大段粘贴正文。
"""


# --------------------------------------------------------------------------
# 2. 终端渲染：一行调用 + 一行结果
# --------------------------------------------------------------------------
DIM, BOLD, GREEN, RED, CYAN, RESET = "\033[2m", "\033[1m", "\033[32m", "\033[31m", "\033[36m", "\033[0m"
PRIMARY_KEYS = ("file_path", "path", "command", "pattern")


def _clip(text: str, limit: int) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _format_tool_call(tool_call: dict) -> str:
    args = tool_call.get("args") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}

    positional, extras = [], []
    for key, value in args.items():
        if key in {"content", "new_string"}:
            extras.append(f"{key}: {len(str(value).splitlines())} 行")
            continue
        shown = _clip(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False), 60)
        if key in PRIMARY_KEYS and not positional:
            positional.append(shown)
        else:
            extras.append(f"{key}={shown}")
    return f"{BOLD}{tool_call.get('name', '?')}{RESET}({DIM}{', '.join(positional + extras)}{RESET})"


def _format_tool_result(message: ToolMessage) -> tuple[str, bool]:
    content = message.content
    if isinstance(content, list):
        content = "\n".join(str(b.get("text", b)) if isinstance(b, dict) else str(b) for b in content)
    text, failed = str(content), getattr(message, "status", None) == "error"
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return "(空)", failed
    summary = _clip(lines[0], 88) + (f"  (+{len(lines) - 1} 行)" if len(lines) > 1 else "")
    return summary, failed


def run(agent, topic: str, thread_id: str) -> None:
    """跑一轮创作+发布，实时打印工具调用链。"""
    config = {"configurable": {"thread_id": thread_id}}
    shown_calls: set[str] = set()
    shown_results: set[str] = set()
    text_pending = False

    for mode, payload in agent.stream(
        {"messages": [{"role": "user", "content": topic}]},
        config,
        stream_mode=["messages", "updates"],
    ):
        if mode == "messages":
            chunk, _meta = payload
            if getattr(chunk, "type", None) == "AIMessageChunk" and isinstance(chunk.content, str) and chunk.content:
                print(chunk.content, end="", flush=True)
                text_pending = True
            continue

        for _node, data in (payload or {}).items():
            for message in (data.get("messages", []) if isinstance(data, dict) else []):
                for tool_call in getattr(message, "tool_calls", None) or []:
                    call_id = tool_call.get("id") or tool_call.get("name")
                    if call_id in shown_calls:
                        continue
                    shown_calls.add(call_id)
                    if text_pending:
                        print()
                        text_pending = False
                    print(f"  {CYAN}●{RESET} {_format_tool_call(tool_call)}", flush=True)

                if isinstance(message, ToolMessage):
                    call_id = getattr(message, "tool_call_id", None) or message.name
                    if call_id in shown_results:
                        continue
                    shown_results.add(call_id)
                    summary, failed = _format_tool_result(message)
                    print(f"  {RED if failed else GREEN}⎿{RESET}  {DIM}{summary}{RESET}", flush=True)

    print("\n")


# --------------------------------------------------------------------------
# 3. 命令行对话
# --------------------------------------------------------------------------
HELP = """可用命令：
  :new    开一个全新的 thread（用来验证 /memory/ 是不是真的跨会话）
  :q      退出
其余输入直接当成创作主题发给 agent。"""


def main() -> None:
    thread_id = f"post-{uuid.uuid4().hex[:6]}"
    agent = build_agent()

    mode = "真实发布" if os.environ.get("DEVTO_API_KEY") else "dry-run（未设置 DEVTO_API_KEY，只做本地校验）"
    print(f"{DIM}发布模式: {mode}{RESET}")
    print(f"{DIM}thread_id: {thread_id}（:new 换会话，:q 退出）{RESET}\n")

    while True:
        try:
            topic = input(f"{CYAN}主题{RESET}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not topic:
            continue
        if topic in {":q", "quit", "exit"}:
            break
        if topic == ":help":
            print(HELP)
            continue
        if topic == ":new":
            thread_id = f"post-{uuid.uuid4().hex[:6]}"
            print(f"{DIM}已切换到全新 thread: {thread_id}{RESET}\n")
            continue
        run(agent, topic, thread_id)

    print(f"{DIM}定稿: {POSTS_DIR}{RESET}")
    print(f"{DIM}归档: {ARCHIVE_DIR}{RESET}")


if __name__ == "__main__":
    main()
