#!/usr/bin/env python3
"""用 TypeSafe 的 Jev 模型（System One）评估 resume.md 与 job-infos/ 下各岗位的匹配度。

用法:
    python3 jev_match.py --dry-run      # 只打印将要发送的请求体，不调用 API
    python3 jev_match.py                # 调用 API，写出 jev-results.json 与 jev-match-report.md
    python3 jev_match.py --only 05 06   # 只评估文件名含 "05" 或 "06" 的岗位

API key 读取顺序: 环境变量 TYPESAFE_API_KEY -> 本目录下的 .env 文件
"""

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
HERE = Path(__file__).resolve().parent
MAX_RETRIES = 4
RETRY_STATUSES = {429, 500, 502, 503, 529}

# Score 的档位：从低到高，描述必须是能独立成立的具象情形。
FIT_LEVELS = [
    "完全不匹配：岗位的核心必备技能与候选人的技能栈没有交集，候选人无法胜任该岗位的主要职责。",
    "弱匹配：仅有少量边缘技能或软性条件吻合，核心必备技能明显缺失，需要一年以上的转岗学习才能胜任。",
    "部分匹配：岗位约一半的要求能够满足，但至少存在一项重要的必备技能或经验短板，需要在补充学习或他人协助下才能开展工作。",
    "较好匹配：绝大多数必备技能与经验要求都能满足，仅有个别非关键项缺失或未在简历中体现。",
    "高度匹配：岗位的必备技能、经验范围与领域背景几乎逐条吻合，候选人可直接胜任，且具备明显的加分项。",
]


def build_questions():
    """基于同一份 state 的独立判断题，一起发出（彼此不可见）。"""
    return {
        "overall_fit": {
            "type": "score",
            "instructions": (
                "给定候选人简历（`resume`）与职位描述（`job`），候选人与该岗位的整体匹配程度如何？"
                "以岗位列出的核心必备要求为主要依据，加分项只作次要参考；"
                "同时考虑候选人的技术方向与岗位所属技术领域是否属于同一方向。"
            ),
            "criteria": FIT_LEVELS,
        },
        "skill_coverage": {
            "type": "choice",
            "instructions": (
                "`job` 列出了一组必备技术技能。判断 `resume` 对这些必备技能的覆盖属于哪一档。"
                "注意区分两种情况：(a) 简历没有写明，但这类技能属于任何有经验的同方向工程师都默认具备的通用工程素养"
                "（例如 Git 版本控制、HTTP 协议、跨浏览器兼容）；"
                "(b) 简历没有写明，且这属于本岗位特有专业方向的技能（例如特定的编程语言、框架、领域经验）。"
            ),
            "criteria": {
                "full": "简历明确写明了岗位要求的全部必备技能。",
                "mostly_generic_only": "简历写明了大部分必备技能，未写明的仅限 (a) 类通用技能，岗位特有的专业必备技能均已覆盖。",
                "missing_specialized": "简历缺少一项或多项 (b) 类岗位特有的专业必备技能，但缺失的不是多数。",
                "missing_most": "简历缺少大部分必备技能，岗位所需的专业方向与候选人方向不同。",
            },
        },
        "specialized_skills_present": {
            "type": "noul",
            "instructions": (
                "岗位所要求的、代表其专业方向（而非任何程序员都具备的通用技能）的核心必备技能，候选人是否已经具备？"
                "只考虑岗位特有的专业能力，不考虑 Git、HTTP 等通用工程素养。"
            ),
            "criteria": {
                "true": "岗位特有的专业方向必备技能，候选人已具备。",
                "false": "岗位特有的专业方向必备技能，候选人明显不具备。",
            },
        },
        "experience_years_met": {
            "type": "choice",
            "instructions": (
                "该岗位对从业年限有要求。依据 `resume` 中的工作经历与项目时间信息，"
                "候选人的经验年限是否达到 `job` 的要求？"
            ),
            "criteria": {
                "met": "简历提供的时间信息足以判断，且年限达到或超过岗位要求。",
                "not_met": "简历提供的时间信息足以判断，且年限低于岗位要求。",
                "unknown": "简历没有提供任何可用于判断从业年限的时间信息（如起止年月、任职公司），无法判断。",
            },
        },
        "education_met": {
            "type": "choice",
            "instructions": (
                "该岗位对学历有要求（可能包含“统招”“全日制”等限定）。依据 `resume` 中的教育信息，"
                "候选人的学历是否满足 `job` 的学历要求？"
            ),
            "criteria": {
                "met": "简历写明的学历与专业满足岗位的学历要求。",
                "not_met": "简历写明的学历或专业不满足岗位的学历要求。",
                "unknown": "简历完全没有提供学历或专业信息，无法判断。",
            },
        },
        "domain_relevance": {
            "type": "noul",
            "instructions": (
                "候选人的技术领域背景（由其技能清单与项目经历体现）是否属于 `job` 所招聘的技术方向？"
                "例如：Web 前端开发、数据可视化、大模型应用，与嵌入式/内核驱动开发、机器视觉、"
                "Java 后端微服务等属于不同的技术方向。"
            ),
            "criteria": {
                "true": "候选人的技术方向与岗位招聘的技术方向属于同一领域。",
                "false": "候选人的技术方向与岗位招聘的技术方向属于不同领域，所需知识体系与工作内容差异很大。",
            },
        },
        "disqualifying_gap": {
            "type": "choice",
            "instructions": (
                "在 `job` 的必备（非加分）要求中，最有可能导致候选人在简历初筛阶段被直接淘汰的单一缺口是哪一个？"
                "若不存在这样的缺口，选择 no_blocker。"
            ),
            "criteria": {
                "no_blocker": "不存在会让候选人在初筛阶段被直接淘汰的必备要求缺口。",
                "programming_language": "岗位指定的编程语言（如 C/C++、C#、Java）候选人不会，其主力语言是 JavaScript/TypeScript。",
                "embedded_hardware": "缺少嵌入式、内核驱动、单板或硬件接口相关经验。",
                "machine_vision": "缺少机器视觉、工业相机、视觉算法平台（Halcon/OpenCV/VisionPro 等）等专业领域经验。",
                "backend_data": "缺少后端数据层经验，如关系型数据库、缓存、消息队列等中间件。",
                "backend_framework": "缺少岗位指定的后端框架或平台，如 Spring Cloud 微服务、Kubernetes 服务编排。",
                "education_or_years": "学历或从业年限不满足岗位的硬性门槛。",
            },
        },
        "resume_sufficiency": {
            "type": "noul",
            "instructions": (
                "`resume` 是否提供了足够的信息，使评估者能对 `job` 的全部硬性要求"
                "（学历、从业年限、所在城市等）做出判断？"
            ),
            "criteria": {
                "true": "简历已包含学历、从业年限等关键信息，足以判断岗位的全部硬性要求。",
                "false": "简历缺少学历、从业年限等关键信息，岗位的部分硬性要求无法判断。",
            },
        },
    }


_SSL_CONTEXT = None


def ssl_context():
    """macOS 上 python.org 版 Python 常缺少 CA 证书，回退到系统信任库（仍保持证书校验）。"""
    global _SSL_CONTEXT
    if _SSL_CONTEXT is None:
        try:
            import certifi

            _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            fallback = next(
                (p for p in ("/etc/ssl/cert.pem", "/usr/local/etc/openssl/cert.pem") if Path(p).exists()),
                None,
            )
            _SSL_CONTEXT = (
                ssl.create_default_context(cafile=fallback)
                if fallback
                else ssl.create_default_context()
            )
    return _SSL_CONTEXT


def load_api_key():
    key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if key:
        return key
    env_file = HERE / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "TYPESAFE_API_KEY":
                return value.strip().strip("'\"")
    return ""


def call_jev(api_key, state, questions, timeout=180):
    """POST 一次评估请求，对 429/5xx 做指数退避重试。"""
    body = json.dumps(
        {"state": state, "model": MODEL, "questions": questions}, ensure_ascii=False
    ).encode("utf-8")
    last_err = None
    for attempt in range(MAX_RETRIES):
        req = urllib.request.Request(
            ENDPOINT,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            if exc.code not in RETRY_STATUSES or attempt == MAX_RETRIES - 1:
                raise SystemExit(f"API 返回 {exc.code}: {detail}") from exc
            last_err = f"HTTP {exc.code}: {detail}"
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == MAX_RETRIES - 1:
                raise SystemExit(f"请求失败: {exc}") from exc
            last_err = str(exc)
        wait = 2 ** attempt
        print(f"    {last_err} — {wait}s 后重试 ({attempt + 1}/{MAX_RETRIES})", file=sys.stderr)
        time.sleep(wait)
    raise SystemExit(f"重试耗尽: {last_err}")


def fmt_pct(x):
    return f"{x:.3f}"


def render_answer(question, answer):
    """把三种 primitive 的回答渲染成 markdown 片段，返回 (单行摘要, 详情行列表)。"""
    qtype = answer.get("type", question["type"])

    if qtype == "noul":
        p = answer.get("noul", 0.0)
        verdict = "是" if p >= 0.5 else "否"
        return f"{verdict} (p={fmt_pct(p)})", [f"P(是) = {fmt_pct(p)}"]

    if qtype == "choice":
        choice = answer.get("choice")
        conf = answer.get("confidence")
        probs = answer.get("probabilities", {})
        top = sorted(probs.items(), key=lambda kv: -kv[1])
        detail = [f"{k}: {fmt_pct(v)}" for k, v in top if v >= 0.01]
        summary = f"`{choice}`"
        if conf is not None:
            summary += f" (confidence={fmt_pct(conf)})"
        return summary, detail

    if qtype == "score":
        score = answer.get("score", 0.0)
        conf = answer.get("confidence")
        legend = answer.get("legend", {}) or {}
        levels = sorted(int(k) for k in legend if str(k).lstrip("-").isdigit())
        hi = max(levels) if levels else 5
        lo = min(levels) if levels else 0
        nearest = min(levels, key=lambda k: abs(k - score)) if levels else None
        label = legend.get(str(nearest), "") if nearest is not None else ""
        summary = f"{score:.2f} / {hi}"
        if conf is not None:
            summary += f" (confidence={fmt_pct(conf)})"
        detail = [f"最接近档位 {nearest}: {label}"] if label else []
        for k in levels:
            v = (answer.get("probabilities", {}) or {}).get(str(k), 0.0)
            detail.append(f"级 {k} ({fmt_pct(v)}): {legend.get(str(k), '')}")
        return summary, detail

    return json.dumps(answer, ensure_ascii=False), []


QUESTION_TITLES = {
    "overall_fit": "整体匹配度",
    "skill_coverage": "必备技能覆盖",
    "specialized_skills_present": "专业方向技能具备",
    "experience_years_met": "年限要求",
    "education_met": "学历要求",
    "domain_relevance": "技术方向相关",
    "disqualifying_gap": "最致命缺口",
    "resume_sufficiency": "简历信息充分",
}

# 总览表里按这个顺序取回答的压缩写法
OVERVIEW_KEYS = [
    "overall_fit",
    "skill_coverage",
    "specialized_skills_present",
    "domain_relevance",
    "experience_years_met",
    "education_met",
    "disqualifying_gap",
]


def compact(question, answer):
    qtype = answer.get("type", question["type"])
    if qtype == "noul":
        p = answer.get("noul", 0.0)
        return f"{'是' if p >= 0.5 else '否'} ({p:.2f})"
    if qtype == "choice":
        return f"{answer.get('choice')}"
    if qtype == "score":
        return f"{answer.get('score', 0):.2f}"
    return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印请求体，不调用 API")
    ap.add_argument("--only", nargs="*", default=None, help="只处理文件名包含这些字符串的岗位")
    ap.add_argument("--json-out", default=str(HERE / "jev-results.json"))
    ap.add_argument("--md-out", default=str(HERE / "jev-match-report.md"))
    args = ap.parse_args()

    resume = (HERE / "resume.md").read_text(encoding="utf-8")
    jobs = sorted((HERE / "job-infos").glob("*.md"))
    if args.only:
        jobs = [j for j in jobs if any(tok in j.name for tok in args.only)]
    if not jobs:
        raise SystemExit("没有找到岗位文件")

    questions = build_questions()

    if args.dry_run:
        sample = {
            "state": {"resume": resume, "job": {"title": jobs[0].stem, "posting": jobs[0].read_text(encoding="utf-8")}},
            "model": MODEL,
            "questions": questions,
        }
        print(json.dumps(sample, ensure_ascii=False, indent=2))
        print(f"\n# dry-run: 共 {len(jobs)} 个岗位，每个岗位 1 次请求", file=sys.stderr)
        return

    api_key = load_api_key()
    if not api_key:
        raise SystemExit(
            "缺少 API key。请任选其一：\n"
            "  1) 在 jev/.env 写入  TYPESAFE_API_KEY=<你的 key>\n"
            "  2) export TYPESAFE_API_KEY=<你的 key>\n"
            "key 可从 https://console.typesafe.ai/keys 获取。"
        )

    results = {}
    total_in = total_out = 0
    for job in jobs:
        title = job.stem
        print(f"[{title}] 评估中...", file=sys.stderr)
        state = {
            "resume": resume,
            "job": {"title": title, "posting": job.read_text(encoding="utf-8")},
        }
        resp = call_jev(api_key, state, questions)
        results[title] = resp
        usage = resp.get("usage", {})
        total_in += usage.get("input_tokens", 0)
        total_out += usage.get("output_tokens", 0)
        print(f"    model={resp.get('model')} tokens={usage}", file=sys.stderr)

    Path(args.json_out).write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Jev 岗位匹配评估报告",
        "",
        f"- 模型：`{next(iter(results.values())).get('model')}`",
        f"- 岗位数：{len(results)}；累计 token：输入 {total_in} / 输出 {total_out}",
        "- 由 `jev_match.py` 调用 TypeSafe System One 端点生成；判断题定义见脚本中的 `build_questions()`。",
        "",
        "## 总览",
        "",
        "| 岗位 | " + " | ".join(QUESTION_TITLES[k] for k in OVERVIEW_KEYS) + " |",
        "| --- | " + " | ".join("---" for _ in OVERVIEW_KEYS) + " |",
    ]
    for title, resp in results.items():
        answers = resp.get("answers", {})
        cells = [compact(questions[k], answers.get(k, {})) for k in OVERVIEW_KEYS]
        lines.append(f"| {title} | " + " | ".join(cells) + " |")

    lines += ["", "## 逐岗位详情", ""]
    for title, resp in results.items():
        answers = resp.get("answers", {})
        lines.append(f"### {title}")
        lines.append("")
        for key, question in questions.items():
            answer = answers.get(key)
            if answer is None:
                continue
            summary, detail = render_answer(question, answer)
            lines.append(f"- **{QUESTION_TITLES[key]}**：{summary}")
            for d in detail:
                lines.append(f"  - {d}")
        lines.append("")

    Path(args.md_out).write_text("\n".join(lines), encoding="utf-8")
    print(f"\n已写出 {args.md_out}\n已写出 {args.json_out}")
    print(f"累计 token：输入 {total_in} / 输出 {total_out}")


if __name__ == "__main__":
    main()
