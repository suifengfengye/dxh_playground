"""一呼百应：1 个主管 + 3 个专家（deepagents subagent 演示）

一句话提问，主管 agent 不自己干活，而是**同时**派出 3 个专家 subagent，
每人带着自己的工具在**各自独立的上下文**里翻完一堆原始资料，
最后只把一份精炼结论交回主管。

这就是 subagent 最核心的价值：上下文隔离。
专家读了几千字的噪声，主管的上下文里只有三句话。

运行：python blog_demo.py
"""

from __future__ import annotations

import random

from langchain.agents.structured_output import ToolStrategy
from langchain_core.callbacks import BaseCallbackHandler
from pydantic import BaseModel, Field

from deepagents import create_deep_agent
from llm import ds_llm

# ===========================================================================
# 1. 三个 mock 工具 —— 故意返回又长又杂的原始资料
#    真实世界里 web_search / 读文件就是这个样子：一屏噪声，有用的就一行。
# ===========================================================================


# 语言 -> (2000 QPS 下的 p99 毫秒, 常驻内存 MB, 冷启动毫秒)
_BASE = {"rust": (3.1, 48, 2), "go": (4.4, 76, 3), "java": (7.8, 512, 380), "python": (41.2, 210, 90)}


def run_benchmark(subject: str) -> str:
    """跑性能压测，返回原始输出。真实的压测日志就长这样：几十上百行，有用的只有几行。"""
    rng = random.Random(42)          # 固定种子，保证每次演示结果一致
    out = [
        f"# benchmark-v3.2 raw dump  subject={subject}",
        "# workload: 高并发 JSON 序列化 + 路由匹配 / 单机 8C16G / 未做任何 JIT 预热",
        "-" * 78,
    ]
    for lang, (p99, rss, boot) in _BASE.items():
        out.append(f"## {lang}  cold_start={boot}ms")
        for qps in (100, 500, 1000, 2000, 5000):
            for run in (1, 2, 3):
                jitter = 1 + rng.uniform(-0.08, 0.12)
                load = 1 + (qps - 100) / 12000        # QPS 越高，p99 越难看
                out.append(
                    f"{lang:<7} qps={qps:<5} run={run}  p50={p99 * jitter / 3:7.2f}ms  "
                    f"p99={p99 * jitter * load:8.2f}ms  rss={int(rss * jitter):5d}MB  err=0  timeout=0"
                )
        out.append("")
    out += [
        "# 原始 csv: 14 个文件位于 /tmp/bench-2026-10-05/ (未随本次结果附上)",
        "# 注意: rust 侧用了 3 处 unsafe 做零拷贝, 这不是同等工作量的裸对比",
        "# 注意: 该 workload 偏 CPU 密集; IO 密集场景下瓶颈在 DB/RPC 等待, 差距会大幅收敛",
    ]
    return "\n".join(out)


_MODULES = [
    "订单", "支付", "账务", "风控", "商品", "库存", "结算", "发票", "用户", "权限",
    "网关", "路由", "配置", "日志", "监控", "告警", "促销", "优惠券", "物流", "售后",
    "客服", "报表", "对账", "清算", "签约", "实名", "消息", "推送", "搜索", "推荐",
    "调度", "任务", "文件", "审计", "灰度", "限流", "熔断", "埋点",
]


def estimate_cost(subject: str) -> str:
    """估算迁移成本，返回逐模块明细。"""
    rng = random.Random(7)
    out = [
        f"# cost-model-v1  subject={subject}",
        "# 团队: 后端 17 人, 其中写过 rust 的 2 人(业余项目级别)",
        "# 学习曲线: 平均 6-10 周达到可交付水平, 期间产能按 40% 计",
        "-" * 62,
        f"{'模块':<6}{'接口数':>8}{'LOC':>8}{'人日':>9}{'风险':>7}",
    ]
    total_loc, total_days = 0, 0.0
    for name in _MODULES:
        loc = rng.randint(600, 4200)
        days = round(loc / 42 * rng.uniform(0.8, 1.6), 1)
        total_loc += loc
        total_days += days
        out.append(f"{name:<6}{rng.randint(4, 22):>8}{loc:>8}{days:>9}{rng.choice(['低', '中', '中', '高', '高']):>7}")
    out += [
        "-" * 62,
        f"合计: {total_loc} LOC / {total_days:.0f} 人日 ≈ {total_days / 21:.1f} 人月",
        f"折算金额: {total_days / 21 * 17:.0f} 万元 (按 17 万/人月)",
        "另需 +2 个月 ramp-up; 重写期业务近乎零交付",
        "隐性成本: 招聘溢价 +30%, 关键路径延期风险高",
        "内部参照: 2024 年那次 go 迁移实际耗时是预估的 2.3 倍",
        "免责: 基于 3 位 TL 的口头估算, 误差 ±50%",
    ]
    return "\n".join(out)


_CRATES = [
    "tokio", "hyper", "axum", "actix-web", "tower", "tonic", "prost", "serde",
    "serde_json", "sqlx", "diesel", "sea-orm", "redis-rs", "rdkafka", "lapin",
    "reqwest", "tracing", "opentelemetry", "prometheus", "metrics", "config",
    "clap", "anyhow", "thiserror", "chrono", "uuid", "regex", "rayon", "dashmap",
    "parking_lot", "bytes", "futures", "async-trait", "governor", "moka",
    "jsonwebtoken", "argon2", "rustls", "ring", "nix",
]


def check_ecosystem(subject: str) -> str:
    """查生态成熟度与已知坑。"""
    rng = random.Random(11)
    out = [
        f"# ecosystem-scan  subject={subject}",
        "# 数据源: crates.io API 快照 2026-10-05 (仅列出本项目可能用到的依赖)",
        "-" * 66,
        f"{'crate':<26}{'下载/月':>12}{'最近更新':>11}{'状态':>12}",
    ]
    for name in _CRATES:
        out.append(
            f"{name:<26}{rng.randint(2, 9000) * 1000:>12,}"
            f"{rng.randint(1, 30):>8} 天前{rng.choice(['活跃', '活跃', '维护中', 'unmaintained']):>12}"
        )
    out += [
        "-" * 66,
        "crate 总量: 18.4 万 | 近 12 个月新增 2.1 万 | 已标记 unmaintained 3400",
        "关键依赖: tonic(gRPC) 成熟; sqlx 可用但生态明显弱于 gorm / mybatis",
        "已知坑 1: async 运行时与 tokio 强绑定, 事后切换成本极高",
        "已知坑 2: 编译时间随项目线性恶化, 大型项目全量编译 8-15 分钟",
        "已知坑 3: 招聘池小, 一线城市 rust 岗位投递量约为 java 的 1/12",
        "长期趋势: 2026 年 rust 已进入 Linux 内核与 Android 主栈, 方向向好",
        "结论倾向: 新项目适合, 存量重写需谨慎",
    ]
    return "\n".join(out)


# ===========================================================================
# 2. 所有专家共用一个结构化输出格式
#    subagent 返回的**不是**它读到的几千字，而是这个对象 —— 主管只看到这里。
# ===========================================================================


class ExpertOpinion(BaseModel):
    """一位专家给出的结论。"""

    conclusion: str = Field(description="一句话结论，不超过 40 字")
    confidence: float = Field(description="置信度，0 到 1 之间")
    key_points: list[str] = Field(description="支撑结论的关键论据，最多 3 条")


def make_expert(name: str, description: str, tool, focus: str) -> dict:
    """把一个工具 + 一段专注方向，打包成一个专家 subagent。"""
    return {
        "name": name,
        "description": description,
        "system_prompt": (
            f"你是一位资深专家，只负责「{focus}」这一个角度。"
            f"调用一次 {tool.__name__} 拿原始数据，然后立刻用结构化输出给出结论。"
            "原始数据里大部分是噪声，你只提炼真正支撑结论的部分。"
            "如果数据不足以支撑判断，就如实降低 confidence。"
        ),
        "tools": [tool],
        "response_format": ToolStrategy(ExpertOpinion),
    }


subagents = [
    make_expert("bench_expert", "负责性能与压测数据的对比分析", run_benchmark, "性能"),
    make_expert("cost_expert", "负责迁移成本与人力投入的估算", estimate_cost, "成本"),
    make_expert("eco_expert", "负责生态成熟度与长期风险的评估", check_ecosystem, "生态风险"),
]

# ===========================================================================
# 3. 主管 agent —— 自己没有工具，只会「派活」和「汇总」
# ===========================================================================

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    subagents=subagents,
    system_prompt=(
        "你是一位技术总监。你自己不查任何资料，也不做任何分析。"
        "收到问题后，用 task 工具把三个专家**一次性全部派出去**（同一轮里发起三个 task 调用），"
        "让他们并行工作。等三份结论都回来后，"
        "综合成一份给 CEO 的决策备忘，格式：一句话建议 / 三条核心依据 / 一条最大风险。"
    ),
)

# ===========================================================================
# 4. 运行 + 渲染
# ===========================================================================

DIM, BOLD, GREEN, CYAN, MAGENTA, YELLOW, RED, RESET = (
    "\033[2m", "\033[1m", "\033[32m", "\033[36m", "\033[35m", "\033[33m", "\033[31m", "\033[0m",
)


class ExpertTracer(BaseCallbackHandler):
    """把 subagent 内部的动静透出来，顺便统计它到底读了多少字。

    `task` 工具内部是同步的 subagent.invoke（deepagents/middleware/subagents.py），
    不是子图，所以 stream_mode 收不到；只有 callback 能拿到。
    metadata 里的 lc_agent_name 就是专家名字，主管自己是 None —— 靠它区分主/子。
    """

    def __init__(self) -> None:
        self._active: dict[object, str] = {}
        self.raw_chars = 0                        # 专家们一共读进来多少字
        self.per_expert: dict[str, int] = {}      # 每个专家各自读了多少

    def on_tool_start(self, serialized, input_str, *, run_id=None, metadata=None, inputs=None, **kwargs):
        who = (metadata or {}).get("lc_agent_name")
        tool = (serialized or {}).get("name", "?")
        if not who or tool == "task":
            return
        self._active[run_id] = who
        arg = ", ".join(str(v)[:40] for v in (inputs or {}).values())
        print(f"    {MAGENTA}│{RESET} {DIM}{who:<12}{RESET} {CYAN}●{RESET} {BOLD}{tool}{RESET}({DIM}{arg}{RESET})", flush=True)

    def on_tool_end(self, output, *, run_id=None, **kwargs):
        who = self._active.pop(run_id, None)
        if who is None:
            return
        text = str(getattr(output, "content", output))
        self.raw_chars += len(text)
        self.per_expert[who] = self.per_expert.get(who, 0) + len(text)
        first = " ".join(text.split())[:70]
        print(f"    {MAGENTA}│{RESET} {DIM}{who:<12}{RESET} {GREEN}⎿{RESET}  {DIM}{first}… [{len(text)} 字]{RESET}", flush=True)


def main() -> None:
    question = "我们明年该不该把主力后端服务重写成 Rust？"
    print(f"\n{BOLD}用户 >>> {question}{RESET}\n")

    tracer = ExpertTracer()
    seen_calls, seen_results = set(), set()
    handed_back = 0                     # 主管真正拿到手的字数

    for mode, payload in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        {"configurable": {"thread_id": "demo-1"}, "callbacks": [tracer]},
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
                        who = (call.get("args") or {}).get("subagent_type", "?")
                        print(f"\n  {YELLOW}▸ 派出专家 {BOLD}{who}{RESET}", flush=True)

                if type(message).__name__ == "ToolMessage":
                    cid = getattr(message, "tool_call_id", None)
                    if cid in seen_results or getattr(message, "name", "") != "task":
                        continue
                    seen_results.add(cid)
                    handed_back += len(str(message.content))
                    verdict = str(message.content).replace("\n", " ")[:110]
                    print(f"    {GREEN}◂ 收回结论{RESET} {DIM}{verdict}…{RESET}", flush=True)

    # ---- 全场最有说服力的一行：上下文隔离到底省了多少 ----
    print(f"\n{BOLD}=== 上下文账单 ==={RESET}")
    for who, chars in tracer.per_expert.items():
        print(f"  {who:<13} 在自己的上下文里读了 {chars:>7,} 字")
    print("  " + "-" * 52)
    print(f"  三位专家合计               读入 {tracer.raw_chars:>7,} 字")
    print(f"  主管最终收到               仅   {handed_back:>7,} 字   {GREEN}{handed_back / max(tracer.raw_chars, 1):.1%}{RESET}")
    print(f"  {DIM}让单个 agent 硬扛，这 {tracer.raw_chars:,} 字会全部压进同一份上下文。{RESET}\n")


if __name__ == "__main__":
    main()
