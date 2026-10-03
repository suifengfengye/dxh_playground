#!/usr/bin/env python3
"""发布脚本：把一篇 markdown 文案发到 dev.to。

由 agent 通过 execute 调用，所以输出必须是「一眼能看懂 + 退出码可判定」的：

    python3 publish.py --file demo.md
    python3 publish.py --file demo.md --tags ai,agent

没设置 DEVTO_API_KEY 时自动走 dry-run：只做本地合规校验 + 打印模拟响应，
不会真的发到外网。文案格式（YAML front matter + markdown 正文）：

    ---
    title: 标题
    tags: ai, agent
    ---
    正文……

退出码：0 成功 / 1 文案不合规 / 2 调用 API 失败
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # workspace/publish.py -> 项目根
POSTS_DIR = BASE_DIR / "posts"
API_URL = "https://dev.to/api/articles"
MAX_TAGS = 4
TAG_RE = re.compile(r"^[a-z0-9]{1,30}$")

# dev.to 前置的 Varnish 边缘层会按 User-Agent 拦截：urllib 的默认 UA
# "Python-urllib/3.x" 会在请求到达 API 之前就被拒，返回一个**没有 body 的空 403**，
# 极容易被误判成「API key 无效」。curl / python-requests / 自定义 UA 都能正常通过，
# 所以这里必须显式带上，不能用默认值。
USER_AGENT = "auto-post-agent/1.0"

# dev.to 的真实约束，agent 必须按这个改稿
MAX_TITLE = 128
MIN_BODY = 200


def fail(result: dict) -> int:
    """按退出码把结果打给 agent 看。"""
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(result.get("exit", 1))


def resolve(path_arg: str) -> Path:
    """接受 /posts/x.md、posts/x.md、x.md、绝对路径四种写法。"""
    raw = Path(path_arg)
    candidates = [raw] if raw.is_absolute() else [Path.cwd() / raw, BASE_DIR / raw]
    name = raw.name
    candidates += [POSTS_DIR / name, POSTS_DIR / raw]
    for cand in candidates:
        if cand.exists():
            return cand
    return POSTS_DIR / name


def parse(text: str) -> tuple[dict[str, str], str]:
    """拆出 front matter 和正文。"""
    if not text.lstrip().startswith("---"):
        return {}, text.strip()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text.strip()
    meta: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip()
    return meta, parts[2].strip()


def validate(meta: dict[str, str], body: str) -> tuple[str, list[str], list[str]]:
    """返回 (title, tags, errors)，errors 非空就不许发。"""
    errors: list[str] = []

    title = meta.get("title", "").strip()
    if not title:
        errors.append("front matter 缺少 title")
    elif len(title) > MAX_TITLE:
        errors.append(f"title 超长：{len(title)} 字 > {MAX_TITLE}")

    if len(body) < MIN_BODY:
        errors.append(f"正文太短：{len(body)} 字 < {MIN_BODY}，dev.to 上撑不起一篇")

    tags = [t.strip().lower() for t in meta.get("tags", "").split(",") if t.strip()]
    if len(tags) > MAX_TAGS:
        errors.append(f"tags 最多 {MAX_TAGS} 个，当前 {len(tags)} 个")
    for tag in tags:
        if not TAG_RE.match(tag):
            errors.append(
                f"非法 tag：{tag!r}，只允许小写字母/数字且不超过 30 字符（中文标签 dev.to 不接受）"
            )

    return title, tags, errors


def retry_after(detail: str) -> int:
    """从 429 的响应体里解析出要等多少秒。"""
    match = re.search(r"in (\d+) seconds?", detail)
    return int(match.group(1)) + 2 if match else 32


def publish(title: str, body: str, tags: list[str], dry_run: bool, retries: int = 2):
    """发一篇文章。返回 (data, error)，error 非空表示失败。"""
    if dry_run:
        return {
            "id": 0,
            "url": "https://dev.to/dry-run（未设置 DEVTO_API_KEY，没有真的发布）",
            "title": title,
            "tags": tags,
        }, None

    payload = json.dumps(
        {"article": {"title": title, "body_markdown": body, "tags": tags, "published": True}}
    ).encode("utf-8")

    for attempt in range(retries + 1):
        request = urllib.request.Request(
            API_URL,
            data=payload,
            headers={
                "api-key": os.environ["DEVTO_API_KEY"],
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8")), None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace").strip()[:400]
            # dev.to 有发布频率限制（连发多篇必然撞上），等一会儿重试一次就好，
            # 这是平台侧的节流，跟文案本身合不合规没关系。
            if exc.code == 429 and attempt < retries:
                wait = retry_after(detail)
                print(f"[retry] 被限流，等待 {wait}s 后重试（{attempt + 1}/{retries}）", file=sys.stderr)
                time.sleep(wait)
                continue
            if exc.code == 403 and not detail:
                detail = (
                    "响应体为空，说明请求在边缘层就被拒了，多半是 User-Agent 被拦截"
                    f"（当前 UA={USER_AGENT}，别改回 urllib 的默认值）"
                )
            return None, {"status": exc.code, "body": detail, "retryable": exc.code == 429}
        except Exception as exc:  # 网络断了、超时……都算 API 失败
            return None, {"error": f"{type(exc).__name__}: {exc}"}

    return None, {"status": 429, "body": "重试次数用尽", "retryable": True}


def main() -> int:
    parser = argparse.ArgumentParser(description="把 markdown 文案发布到 dev.to")
    parser.add_argument("--file", required=True, help="文案路径，如 demo.md")
    parser.add_argument("--dry-run", action="store_true", help="只校验不真发")
    args = parser.parse_args()

    path = resolve(args.file)
    if not path.exists():
        return fail({"ok": False, "exit": 1, "step": "locate", "error": f"找不到文案：{args.file}"})

    meta, body = parse(path.read_text(encoding="utf-8"))
    title, tags, errors = validate(meta, body)
    if errors:
        return fail({"ok": False, "exit": 1, "step": "validate", "file": path.name, "errors": errors})

    dry_run = args.dry_run or not os.environ.get("DEVTO_API_KEY")
    data, error = publish(title, body, tags, dry_run)
    if error:
        result = {"ok": False, "exit": 2, "step": "api", "file": path.name, **error}
        if error.get("retryable"):
            result["hint"] = "429 是平台限流，文案本身没问题，不要改文案；等一会儿原样重跑即可"
        return fail(result)

    print(
        json.dumps(
            {
                "ok": True,
                "exit": 0,
                "dry_run": dry_run,
                "file": path.name,
                "title": title,
                "tags": tags,
                "url": data.get("url"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
