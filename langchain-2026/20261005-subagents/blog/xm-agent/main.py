"""一个主管 + N 个子代理：输入几个 X 账号，就并行派出几个子代理。

和 blog_demo.py 的关键区别在 **N 由用户输入决定**：

    subagents 列表里永远只有 **一个** x_account_reporter 类型定义，
    N 个实例是靠主管在同一轮里发出 N 次 task 调用来产生的。

用户输入 2 个账号就看到 2 条并行，输入 5 个就看到 5 条 —— 动态性来自
「调用次数」，不是「定义数量」。这正是 subagent 的教科书用法：一个类型，N 个实例。

运行：
    python main.py                              # 用默认的两个演示账号
    python main.py 账号名 [更多账号...]          # 自己指定，mock 下传什么都能跑

数据源：
    配了 TWITTERAPI_IO_KEY 就走 twitterapi.io 真实接口，此时账号名必须是
    X 上真实存在的（不带 @）；
    没配就用内置 mock —— 账号与推文内容**均为虚构**，X 上搜不到，
    传任意名字都能跑通（未预置的账号会走通用模板）。

依赖：
    llm.py / x_api.py 都在本目录，这个文件夹可以整个拷走单独运行，
    不依赖仓库里其他任何文件。
"""

from __future__ import annotations

import os
import re
import sys
import time
from langchain.agents.structured_output import ToolStrategy
from langchain_core.callbacks import BaseCallbackHandler
from pydantic import BaseModel, Field

from deepagents import create_deep_agent
from llm import ds_llm
from x_api import fetch_user_tweets

# 假账号，根据实际情况调整
DEFAULT_ACCOUNTS = ["nova_rocket", "quant_whale"]

# ===========================================================================
# 1. 子代理要交回来的东西 —— 主管只会看到这个对象，看不到上万个字符的原始 JSON
# ===========================================================================


class TweetItem(BaseModel):
    """一条推文，只保留人真正会看的那几个字段。"""

    time: str = Field(description="发布时间，格式 HH:MM，24 小时制")
    content: str = Field(description="推文正文，去掉链接、@ 和多余空白")
    likes: int = Field(description="点赞数")
    reposts: int = Field(description="转发数")
    is_repost: bool = Field(description="是否为自己转发的他人内容")


class AccountReport(BaseModel):
    """一个账号当天的动态。"""

    username: str = Field(description="账号用户名，不带 @")
    display_name: str = Field(description="账号显示名")
    tweet_count: int = Field(description="当天发布的推文条数")
    tweets: list[TweetItem] = Field(description="当天发布的推文，按时间升序排列")
    summary: str = Field(description="一句话概括这个账号当天的动向，不超过 60 字")
    note: str = Field(description="异常说明，如“当天无更新”或接口报错；正常时留空字符串")


# ===========================================================================
# 2. 只定义「一个类型」。N 个实例靠主管发 N 次 task 得到。
# ===========================================================================

X_REPORTER: dict = {
    "name": "x_account_reporter",
    "description": (
        "拉取并整理某一个 X 账号当天的动态。"
        "每调用一次只处理一个账号；要查多个账号，就把它调用多次。"
    ),
    "system_prompt": (
        "你只负责一个 X 账号，不要处理账号以外的任何话题。\n"
        "步骤：\n"
        "1. 调用 fetch_user_tweets 一次，拿到该账号最近的原始推文数据。\n"
        "2. 只保留 is_today 为 true 的推文，其余一律丢弃。\n"
        "3. 原始数据里一条推文有十几个字段，绝大多数是噪声，"
        "你只提取正文、时间、点赞数、转发数、是否转推这五项。\n"
        "4. 时间统一换成 HH:MM 格式。\n"
        "5. 如果当天一条都没有，tweet_count 填 0、tweets 留空，"
        "并在 note 里写明「当天无更新」。\n"
        "严禁编造任何推文内容，一切以工具返回的数据为准。"
    ),
    "tools": [fetch_user_tweets],
    "response_format": ToolStrategy(AccountReport),
}

# ===========================================================================
# 3. 主管：自己没有工具，只负责「按账号数量派活」和「汇总」
# ===========================================================================

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    subagents=[X_REPORTER],
    system_prompt=(
        "你是 X 动态汇总助手。用户会给你若干个 X 账号名。\n"
        "必须遵守：\n"
        "1. 对**每一个**账号单独调用一次 task 工具，subagent_type 固定填 x_account_reporter，"
        "把账号名放进 description 里，例如「拉取 nova_rocket 今天的动态」。\n"
        "2. 所有 task 调用必须放在**同一轮里一次性发出**，让它们并行跑，"
        "不要发一个等一个。有几个账号就发几次。\n"
        "3. 不允许使用 general-purpose 子代理，也不允许自己编造或猜测任何推文内容。\n"
        "4. 等全部返回后，用中文 Markdown 输出汇总报告，格式：\n"
        "   - 开头一个总览表格：账号 | 当天条数 | 一句话概要\n"
        "   - 然后每个账号一节，二级标题是「@账号名（显示名）」，"
        "下面用一个表格列出当天的推文：时间 | 内容 | 点赞 | 转发 | 转推\n"
        "   - 最后加一行小字说明数据来源\n"
        "5. 全程使用中文，不要输出英文。"
    ),
)

# ===========================================================================
# 4. 运行 + 渲染
# ===========================================================================

DIM, BOLD, GREEN, CYAN, MAGENTA, YELLOW, RESET = (
    "\033[2m", "\033[1m", "\033[32m", "\033[36m", "\033[35m", "\033[33m", "\033[0m",
)


def _reported_account(output, fallback: str) -> str:
    """从 task 的返回值里取出账号名。

    子代理交回来的是一段 JSON（AccountReport），里面就有 username 字段，
    比去猜 description 里哪个词是账号名可靠得多。
    """
    update = getattr(output, "update", None) or {}
    for message in update.get("messages") or []:
        match = re.search(r'"username"\s*:\s*"([^"]+)"', str(getattr(message, "content", "")))
        if match:
            return match.group(1)
    return fallback or "?"


class Trace(BaseCallbackHandler):
    """记录每个子代理读了多长的原始数据、跑了多久。

    `task` 工具内部是同步的 subagent.invoke，不是子图，
    所以 stream_mode 收不到子代理内部的动作，只有 callback 能拿到。
    """

    def __init__(self) -> None:
        self._active: dict[object, str] = {}
        self._task_start: dict[object, tuple[float, str]] = {}
        self.raw_chars: dict[str, int] = {}               # 每个子代理读进来多少字
        self.spans: list[tuple[str, float, float]] = []   # (账号, 开始时刻, 结束时刻)

    def on_tool_start(self, serialized, input_str, *, run_id=None, metadata=None, inputs=None, **kwargs):
        tool = (serialized or {}).get("name", "?")
        args = inputs or {}

        if tool == "task":
            # 先记下起点，账号名等返回值到了再解析
            self._task_start[run_id] = (time.perf_counter(), str(args.get("description", ""))[:20])
            return

        if tool == "fetch_user_tweets":
            user = str(args.get("username", "?"))
            self._active[run_id] = user
            print(f"    {MAGENTA}│{RESET} {DIM}@{user:<13}{RESET} {CYAN}●{RESET} {BOLD}{tool}{RESET}({DIM}{user}{RESET})", flush=True)

    def on_tool_end(self, output, *, run_id=None, **kwargs):
        if run_id in self._task_start:
            start, fallback = self._task_start.pop(run_id)
            self.spans.append((_reported_account(output, fallback), start, time.perf_counter()))
            return

        who = self._active.pop(run_id, None)
        if who is None:
            return
        text = str(getattr(output, "content", output))
        self.raw_chars[who] = self.raw_chars.get(who, 0) + len(text)
        print(
            f"    {MAGENTA}│{RESET} {DIM}@{who:<13}{RESET} {GREEN}⎿{RESET}  "
            f"{DIM}读入 {len(text):,} 字原始 JSON{RESET}",
            flush=True,
        )


def main() -> None:
    accounts = sys.argv[1:] or DEFAULT_ACCOUNTS
    live = bool(os.environ.get("TWITTERAPI_IO_KEY"))

    print(f"\n{BOLD}用户 >>> 看看 {'、'.join('@' + a for a in accounts)} 今天都发了什么{RESET}")
    if live:
        print(f"{DIM}数据源: twitterapi.io 实时接口{RESET}\n")
    else:
        print(f"{BOLD}数据源: mock 演示数据{RESET} {DIM}—— 账号和推文均为虚构，X 上搜不到，传任意名字都能跑{RESET}")
        print(f"{DIM}想看真实数据：export TWITTERAPI_IO_KEY=你的key 后重新运行{RESET}\n")

    trace = Trace()
    seen_calls, seen_results = set(), set()
    handed_back = 0                     # 主管真正拿到手的字符数
    started = time.perf_counter()

    for mode, payload in agent.stream(
        {"messages": [{"role": "user", "content": f"请汇总这些 X 账号今天的动态：{', '.join(accounts)}"}]},
        {"configurable": {"thread_id": "xm-demo"}, "callbacks": [trace]},
        stream_mode=["messages", "updates"],
    ):
        if mode == "messages":
            chunk, _meta = payload
            if getattr(chunk, "type", None) == "AIMessageChunk" and isinstance(chunk.content, str):
                print(chunk.content, end="", flush=True)
            continue

        for _node, data in (payload or {}).items():
            for message in (data.get("messages", []) if isinstance(data, dict) else []):
                for call in getattr(message, "tool_calls", None) or []:
                    if call.get("id") in seen_calls:
                        continue
                    seen_calls.add(call.get("id"))
                    if call.get("name") == "task":
                        desc = str((call.get("args") or {}).get("description", ""))
                        print(f"\n  {YELLOW}▸ 派出子代理{RESET} {BOLD}x_account_reporter{RESET}  {DIM}{desc[:46]}{RESET}", flush=True)

                if type(message).__name__ == "ToolMessage":
                    cid = getattr(message, "tool_call_id", None)
                    if cid in seen_results or getattr(message, "name", "") != "task":
                        continue
                    seen_results.add(cid)
                    handed_back += len(str(message.content))

    wall = time.perf_counter() - started

    # ---- 上下文账单：这个例子最有说服力的地方 ----
    total_raw = sum(trace.raw_chars.values())
    print(f"\n\n{BOLD}=== 上下文账单 ==={RESET}")
    for who, chars in trace.raw_chars.items():
        print(f"  @{who:<14} 在自己的上下文里读了 {chars:>7,} 字")
    print("  " + "-" * 52)
    print(f"  子代理合计               读入 {total_raw:>7,} 字")
    print(f"  主管最终收到             仅   {handed_back:>7,} 字   {GREEN}{handed_back / max(total_raw, 1):.1%}{RESET}")

    # ---- 并行验证：看每段在时间轴上有没有重叠 ----
    if trace.spans:
        spans = sorted(trace.spans, key=lambda span: span[1])
        base = spans[0][1]
        serial = sum(end - start for _, start, end in spans)
        union = max(end for _, _, end in spans) - base

        print(f"\n{BOLD}=== 并行验证（每个子代理占用的时间轴）{RESET}")
        for who, start, end in spans:
            print(f"  @{who:<14}{' ' * int((start - base) * 6)}{'━' * max(1, int((end - start) * 6))}"
                  f"  {start - base:.2f}s → {end - base:.2f}s")
        print("  " + "-" * 52)
        print(f"  各自耗时合计 {serial:.2f}s，但在时间轴上只占用了 {union:.2f}s")
        print(f"  {GREEN}重叠 {serial - union:.2f}s —— 这几段确实是同时在跑的{RESET}")
        print(f"  {DIM}（整个流程含主管的两次模型调用，共 {wall:.2f}s）{RESET}\n")


if __name__ == "__main__":
    main()
