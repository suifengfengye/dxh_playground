from curses import flash
import json

from langchain.messages import ToolMessage

from agent_04 import agent

thread_config = {"configurable": {"thread_id": "1"}}

DIM = "\033[2m" # 浅色
BOLD = "\033[1m" # 加粗
GREEN = "\033[32m" # 绿色
RED = "\033[31m" # 红色
CYAN = "\033[36m" # 青色 / 蓝绿色
RESET = "\033[0m" # 重置

BULLET = "●"   # 工具调用
RESULT = "⎿"   # 工具结果

MAX_ARG = 60      # 单个参数最多显示多少字符
MAX_RESULT = 88   # 结果摘要最多显示多少字符

def _to_text(content) -> str:
    """ 将 content 转换成字符串 """
    if isinstance(content, str):
        return content
    
    if isinstance(content, list):
        parts = []
        for block in content:
            inner = str(block.get("text", block)) if isinstance(block, dict) else str(block)
            parts.append(inner)
        return "\n".join(parts)
    
    return str(content)

def _clip(text: str, limit: int):
    """ 长文本处理：1. 多行转换成一行；2. 超过 limit 之后, ... 处理 """
    text = " ".join(text.split())
    return text if len(text) <= limit  else text[:limit] + "..."

"""
例子：
{'name': 'ls', 'args': {'path': '/'}, 'id': 'call_00_Zx46wkB5FQzlsBkcn84z9263', 'type': 'tool_call'}
"""
# 这些是工具的"主要参数"：直接显示值（如 Read(agent_01.py)），不加 key=
PRIMARY_KEYS = ("file_path", "path", "pattern", "command", "cmd", "query", "url")
def format_tool_call(tool_call: dict):
    # 1. 获取 args,并处理好
    args = tool_call.get('args')
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            args = {}
    # 2. 遍历 args ，处理 位置参数 和 关键字参数，以及 content 参数特殊处理（因为内容会比较多）
    positional: list[str] = []
    extra: list[str] = []
    for key, value in args.items():
        if key == 'content':
            text = value if isinstance(value, str) else str(value)
            extra.append(f"content:{len(text.splitlines())}行")
            continue
        shown = _clip(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False), MAX_ARG)
        if key in PRIMARY_KEYS:
            positional.append(shown)
        else:
            extra.append(f"{key}={shown}")
    # 3. 返回可以在CLI上展示的结果字符串
    arg_text = ", ".join(positional + extra)
    return f"{BOLD}{tool_call.get('name', '?')}{RESET}({DIM}{arg_text}{RESET})"


def format_tool_result(message: ToolMessage) -> tuple[str, bool]:
    """渲染工具结果，返回 (摘要文本, 是否失败)。"""
    # 1. 获取 message.content 的文本，全部转换成字符串;以及 status 
    text = _to_text(message.content)
    failed = getattr(message, 'status', None) == 'error'

    # 2. 如果以 "[" 开头，说明是列表，直接返回 "X项"
    stripped = text.strip()
    if not failed and stripped.startswith("["):
        try:
            return f"{len(json.loads(stripped))} 项", False
        except json.JSONDecodeError:
            pass

    # 3. 处理空，一行/多行的情况
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return "(空)", failed

    summary = _clip(lines[0], MAX_RESULT)
    if len(lines) > 1:
        summary += f" (+{len(lines) - 1}行)"
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

    for mode, payload in resp_stream:
        # print(f"mode:{mode}, payload:{payload}")
        if mode == "messages":
            chunk, _metadata = payload or ()
            if getattr(chunk, 'type', None) != "AIMessageChunk":
                continue
            if isinstance(chunk.content, str) and chunk.content:
                print(chunk.content, end="", flush=True)
                text_pending = True

        if mode == "updates":
            # print(f"updates 0: {payload}")
            for _node, data in (payload or {}).items():
                messages = data.get("messages", []) if isinstance(data, dict) else []
                for message in messages:
                    # 1. 针对 AIMessage 的 tool_calls 进行处理
                    for tool_call in getattr(message, "tool_calls", []):
                        if text_pending:
                            print()
                            text_pending = False
                        print(f"    {CYAN}{BULLET}{RESET} {format_tool_call(tool_call)}<- id: {tool_call.get('id', '?')}")
                    # 2. 针对 ToolMessage 处理，ToolMessage是AIMessage中的 tool_calls 对应的调用记录
                    if isinstance(message, ToolMessage):
                        if text_pending:
                            print()
                            text_pending = False
                        summary, failed = format_tool_result(message)
                        color = RED if failed else GREEN
                        print(f"    {color}{RESULT}{RESET} {DIM}{summary}{RESET} <- id: {getattr(message, 'tool_call_id', '?')}")
    print("\n")