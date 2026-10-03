"""FastAPI 服务端：SSE 推送两边进度 + 托管前端。

启动：
    ./run.sh                    # 默认端口 8391
    PORT=9000 ./run.sh          # 换端口

然后打开 http://localhost:8391 —— 前后端同源，不需要处理 CORS。
"""

import asyncio
import json
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

import ds_job_match
import jev_job_match
from job_data import load_jobs, load_resume

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="JEV vs LLM 岗位匹配耗时对比")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _warmup_quietly(warmup) -> None:
    """预热失败不阻断流程，让正式请求自己去报错。"""
    try:
        await warmup()
    except Exception:
        pass


@app.get("/api/jobs")
def list_jobs() -> list[dict]:
    return [{"id": job["id"], "title": job["title"]} for job in load_jobs()]


@app.get("/api/run")
async def run() -> StreamingResponse:
    async def stream():
        jobs = load_jobs()
        resume = load_resume()
        total = len(jobs)
        summaries: dict[str, dict] = {}
        queue: asyncio.Queue = asyncio.Queue()

        async def emit(event: str, data: dict) -> None:
            await queue.put((event, data))

        async def jev_side() -> None:
            try:
                start = time.perf_counter()
                outcome = await jev_job_match.match_all(jobs, resume)
                elapsed = (time.perf_counter() - start) * 1000
                summaries["jev"] = {"total_ms": elapsed, "per_item_ms": elapsed / total}
                await emit(
                    "progress",
                    {
                        "side": "jev",
                        "done": total,
                        "total": total,
                        "elapsed_ms": elapsed,
                        "results": outcome["results"],
                    },
                )
                await emit("side_done", {"side": "jev", **summaries["jev"]})
            except Exception as exc:
                await emit("side_error", {"side": "jev", "message": f"{type(exc).__name__}: {exc}"})

        async def llm_side() -> None:
            try:
                start = time.perf_counter()
                for index, job in enumerate(jobs, start=1):
                    result = await ds_job_match.is_match(job, resume)
                    await emit(
                        "progress",
                        {
                            "side": "llm",
                            "done": index,
                            "total": total,
                            "elapsed_ms": (time.perf_counter() - start) * 1000,
                            "results": [result],
                        },
                    )
                elapsed = (time.perf_counter() - start) * 1000
                summaries["llm"] = {"total_ms": elapsed, "per_item_ms": elapsed / total}
                await emit("side_done", {"side": "llm", **summaries["llm"]})
            except Exception as exc:
                await emit("side_error", {"side": "llm", "message": f"{type(exc).__name__}: {exc}"})

        async def runner() -> None:
            await asyncio.gather(jev_side(), llm_side())
            await queue.put(None)

        yield _sse("status", {"message": "预热中，不计入耗时…"})

        # 预热必须在 start 之前完成 —— 否则浏览器上的计时会把握手成本算进去。
        # JEV 只发一次请求，这部分成本占它总耗时的比例很大，不预热等于在坑它。
        await asyncio.gather(
            _warmup_quietly(jev_job_match.warmup),
            _warmup_quietly(ds_job_match.warmup),
        )

        yield _sse(
            "start",
            {"total": total, "jobs": [{"id": j["id"], "title": j["title"]} for j in jobs]},
        )

        task = asyncio.create_task(runner())
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                event, data = item
                yield _sse(event, data)

            jev_total = summaries.get("jev", {}).get("total_ms")
            llm_total = summaries.get("llm", {}).get("total_ms")
            speedup = llm_total / jev_total if jev_total and llm_total else None
            yield _sse("done", {"summaries": summaries, "speedup": speedup})
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # 关掉可能存在的反向代理缓冲，保证事件即时到达
            "X-Accel-Buffering": "no",
        },
    )


# 静态前端挂到最后，避免抢占 /api 路由
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
