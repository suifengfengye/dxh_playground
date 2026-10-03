import json

from langchain.messages import ToolMessage

from agent_04 import agent

thread_config = {"configurable": {"thread_id": "1"}}

# ---------------------------------------------------------------------------
# 终端样式：模仿 claude code 的"一行调用 + 一行结果"风格
# ---------------------------------------------------------------------------
DIM = "\033[2m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"
RESET = "\033[0m"

BULLET = "●"   # 工具调用
RESULT = "⎿"   # 工具结果

MAX_ARG = 60      # 单个参数最多显示多少字符
MAX_RESULT = 88   # 结果摘要最多显示多少字符

# 这些是工具的"主要参数"：直接显示值（如 Read(agent_01.py)），不加 key=
PRIMARY_KEYS = ("file_path", "path", "pattern", "command", "cmd", "query", "url")


def _to_text(content) -> str:
    """ToolMessage 的 content 可能是字符串，也可能是一堆文本块。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            parts.append(str(block.get("text", block)) if isinstance(block, dict) else str(block))
        return "\n".join(parts)
    return str(content)


def _clip(text: str, limit: int) -> str:
    """压成一行并截断，超长补省略号。"""
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def format_tool_call(tool_call: dict) -> str:
    """把一次工具调用渲染成 `● Read(agent_01.py)` 这样的一行。"""
    args = tool_call.get("args") or {}
    if isinstance(args, str):  # 流式阶段 args 可能是半截 JSON
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            args = {}

    positional: list[str] = []
    extras: list[str] = []
    for key, value in args.items():
        if key == "content":  # 文件内容太长，只报行数
            text = value if isinstance(value, str) else str(value)
            extras.append(f"content: {len(text.splitlines())} 行")
            continue
        shown = _clip(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False), MAX_ARG)
        if key in PRIMARY_KEYS and not positional:
            positional.append(shown)
        else:
            extras.append(f"{key}={shown}")

    inner = ", ".join(positional + extras)
    return f"{BOLD}{tool_call.get('name', '?')}{RESET}({DIM}{inner}{RESET})"


def format_tool_result(message: ToolMessage) -> tuple[str, bool]:
    """渲染工具结果，返回 (摘要文本, 是否失败)。"""
    text = _to_text(message.content)
    failed = getattr(message, "status", None) == "error"

    stripped = text.strip()
    if not failed and stripped.startswith("["):  # ls / glob 返回的是 JSON 数组
        try:
            return f"{len(json.loads(stripped))} 项", False
        except json.JSONDecodeError:
            pass

    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return "(空)", failed

    summary = _clip(lines[0], MAX_RESULT)
    if len(lines) > 1:
        summary += f"  (+{len(lines) - 1} 行)"
    return summary, failed

while True:
    try:
        user_input = input("用户>>>: ")
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if user_input.strip().lower() in {"exit", "quit", "q"}:
        break

    # 两个模式配合：messages 只给模型 token（含半截的 tool_call_chunks，参数不全），
    # updates 才给出"完整的工具调用参数"和"工具返回值"，渲染信息靠它。
    resp_stream = agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        thread_config,
        stream_mode=["messages", "updates"],
    )
    print("Agent>>>: ", end="")

    text_pending = False          # 是否刚打过没有换行的正文
    shown_calls: set[str] = set()    # 去重：同一次调用别打印两遍
    shown_results: set[str] = set()

    for mode, payload in resp_stream:
        # ---- 模型 token：原样流式打印 ----
        if mode == "messages":
            chunk, _metadata = payload
            # 工具结果在 updates 里已经处理，这里只打模型正文，避免重复
            if getattr(chunk, "type", None) != "AIMessageChunk":
                continue
            if isinstance(chunk.content, str) and chunk.content:
                print(chunk.content, end="", flush=True)
                text_pending = True
            continue

        # ---- 节点更新：完整的工具调用与工具结果 ----
        for _node, data in (payload or {}).items():
            messages = data.get("messages", []) if isinstance(data, dict) else []
            for message in messages:
                for tool_call in getattr(message, "tool_calls", None) or []:
                    call_id = tool_call.get("id") or tool_call.get("name")
                    if call_id in shown_calls:
                        continue
                    shown_calls.add(call_id)
                    if text_pending:
                        print()
                        text_pending = False
                    print(f"  {CYAN}{BULLET}{RESET} {format_tool_call(tool_call)}", flush=True)

                if isinstance(message, ToolMessage):
                    call_id = getattr(message, "tool_call_id", None) or message.name
                    if call_id in shown_results:
                        continue
                    shown_results.add(call_id)
                    summary, failed = format_tool_result(message)
                    color = RED if failed else GREEN
                    if text_pending:
                        print()
                        text_pending = False
                    print(f"  {color}{RESULT}{RESET}  {DIM}{summary}{RESET}", flush=True)

    print("\n")