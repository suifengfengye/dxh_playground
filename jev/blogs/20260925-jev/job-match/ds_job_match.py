"""DeepSeek 侧：每个岗位单独一次调用，判断简历与该岗位是否匹配。

对比口径：单次调用 · 直接出结论（关闭思考模式）。

这里每个岗位发一次请求，而不是把 6 个岗位塞进一次调用 —— 后者容易让上下文串味，
且一次性吐出 6 个判断的 JSON 输出可靠性明显下降。每岗位一次是更常规的工程做法。
"""

import json
import re
import time
from pathlib import Path

from dotenv import dotenv_values
from openai import AsyncOpenAI

env_config = dotenv_values(Path(__file__).resolve().parent / ".env")

MODEL = "deepseek-flash"

# 判断标准与 jev_job_match 保持完全一致，否则两边比较的不是同一件事。
CRITERIA = {
    "true": "岗位的核心必备技能与经验年限、学历等硬性要求基本满足，候选人可胜任该岗位的主要职责。",
    "false": "岗位的核心必备技能与候选人的技能栈明显不匹配，或缺失多项关键要求，无法直接胜任。",
}

# DeepSeek 的 JSON 输出模式要求 prompt 里出现 "json" 字样，并给出期望的结构示例。
PROMPT = """请判断候选人简历与岗位要求是否匹配。

判断标准：
- 匹配：{true_criteria}
- 不匹配：{false_criteria}

岗位名称：{title}
岗位描述：
{job}

候选人简历：
{resume}

请只输出 json，不要输出任何其他内容：
{{"is_match": true}}
"""


def _make_client() -> AsyncOpenAI | None:
    api_key = (env_config or {}).get("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    return AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")


client = _make_client()


def _extract_json(text: str) -> str:
    """模型偶尔会把 JSON 包在 ```json 围栏里，先剥掉。"""
    fenced = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    if fenced:
        return fenced.group(1).strip()
    return text.strip()


def _parse_is_match(content: str | None) -> bool:
    """从模型输出里抠出布尔值。

    LLM 返回的是自由文本，需要剥围栏、兜底正则、类型判断三层容错；
    JEV 那边返回的是类型化答案，不存在这一步。
    """
    if not content or not content.strip():
        # DeepSeek 的 JSON 模式本身就会偶发返回空内容
        raise ValueError("模型返回了空内容")

    text = _extract_json(content)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        matched = re.search(r"\{.*\}", text, re.S)
        if not matched:
            raise ValueError(f"输出中找不到 JSON：{content[:200]!r}") from None
        data = json.loads(matched.group(0))

    value = data.get("is_match")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "是", "匹配"}
    raise ValueError(f"is_match 不是布尔值：{value!r}")


async def warmup() -> None:
    """预热：提前把 TLS 握手和模型冷启动的成本消耗掉。"""
    if client is None:
        return
    await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=1,
        extra_body={"thinking": {"type": "disabled"}},
    )


async def is_match(job: dict, resume: str) -> dict:
    """判断单个岗位，返回 {id, title, match, ms, raw, error}。

    解析失败时 match 为 None 并把原因放进 error，不重试 ——
    重试会把耗时算进去，这里要的是「一次调用能不能给出可用结论」。
    """
    if client is None:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY，请在 job-match/.env 中配置")

    prompt = PROMPT.format(
        true_criteria=CRITERIA["true"],
        false_criteria=CRITERIA["false"],
        title=job["title"],
        job=job["text"],
        resume=resume,
    )

    start = time.perf_counter()
    content = None
    match = None
    error = None
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            extra_body={"thinking": {"type": "disabled"}},
            max_tokens=256,
            stream=False,
        )
        content = response.choices[0].message.content
        match = _parse_is_match(content)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "id": job["id"],
        "title": job["title"],
        "match": match,
        "ms": elapsed_ms,
        "raw": content,
        "error": error,
    }
