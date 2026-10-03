"""JEV 侧：一次请求返回全部岗位的匹配判断。

对比口径：单次调用 · 直接出结论。

JEV（TypeSafe System One）原生支持在同一次请求里并行评估多个独立问题，
并且把所有提问合并成一次调用基本不增加响应时间。所以这里把 6 个岗位的判断
全部塞进一次 system_one 调用。
"""

import time
from pathlib import Path

from dotenv import dotenv_values
from typesafe_sdk import AsyncTypeSafeClient, Noul

env_config = dotenv_values(Path(__file__).resolve().parent / ".env")

MODEL = "jev-latest"

# 判断标准与 ds_job_match 保持完全一致，否则两边比较的不是同一件事。
CRITERIA = {
    "true": "岗位的核心必备技能与经验年限、学历等硬性要求基本满足，候选人可胜任该岗位的主要职责。",
    "false": "岗位的核心必备技能与候选人的技能栈明显不匹配，或缺失多项关键要求，无法直接胜任。",
}

# Noul 返回的是「匹配」的概率，这里按 0.5 切成布尔值。
MATCH_THRESHOLD = 0.5


def _make_client() -> AsyncTypeSafeClient | None:
    api_key = (env_config or {}).get("TYPESAFE_API_KEY")
    if not api_key:
        return None
    return AsyncTypeSafeClient(api_key=api_key)


client = _make_client()


def build_request(resume: str, jobs: list[dict]) -> tuple[dict, dict]:
    """构造一次请求所需的 state 与 questions。

    每个岗位放进一个具名字段（`job_01`、`job_02`…），并各配一个独立的 Noul 问题。
    用命名字段而不是数组下标，是因为文档建议「上下文有多部分时优先用具名 JSON 字段」，
    引用起来也比 `jobs[0]` 这种下标更稳。
    """
    state: dict = {"resume": resume}
    questions: dict = {}

    for index, job in enumerate(jobs, start=1):
        key = f"job_{index:02d}"
        state[key] = {"title": job["title"], "jd": job["text"]}
        questions[f"match_{index:02d}"] = Noul(
            instructions=(
                f"候选人简历 `resume` 与职位 `{key}` 的要求匹配吗？"
                "以该职位列出的核心必备技能、经验年限、学历等硬性要求为主要依据；"
                "加分项只作次要参考。"
            ),
            criteria=CRITERIA,
        )

    return state, questions


async def warmup() -> None:
    """预热：提前把 TLS 握手和模型冷启动的成本消耗掉。

    JEV 只发一次请求，握手成本占它总耗时的比例很大，不预热等于在坑它。
    """
    if client is None:
        return
    await client.system_one(
        state={"note": "这是一次预热请求，用于建立连接。"},
        questions={"ok": Noul(instructions="这是一次预热请求，回答「是」即可。")},
        model=MODEL,
        timeout=60.0,
    )


async def match_all(jobs: list[dict], resume: str) -> dict:
    """一次请求判断全部岗位。

    返回 {"results": [{id, title, match, prob, ms, error}], "ms": 总耗时}。
    """
    if client is None:
        raise RuntimeError("缺少 TYPESAFE_API_KEY，请在 job-match/.env 中配置")

    state, questions = build_request(resume, jobs)

    start = time.perf_counter()
    response = await client.system_one(
        state=state,
        questions=questions,
        model=MODEL,
        timeout=120.0,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    results = []
    for index, job in enumerate(jobs, start=1):
        probability = response.nouls[f"match_{index:02d}"].noul
        results.append(
            {
                "id": job["id"],
                "title": job["title"],
                "match": probability > MATCH_THRESHOLD,
                "prob": probability,
                "ms": elapsed_ms,
                "error": None,
            }
        )

    return {"results": results, "ms": elapsed_ms}
