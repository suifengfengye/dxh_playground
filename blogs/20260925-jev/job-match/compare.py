"""命令行跑一遍完整对比 —— 录屏前先用它自测，避免现场翻车。

用法：
    .venv/bin/python compare.py              # 跑一次，看明细
    .venv/bin/python compare.py --repeat 5   # 跑 5 次，给中位数和区间

为什么需要 --repeat：JEV 单次绝对耗时只有几百毫秒，网络抖动占它总耗时的比例很大，
单跑一次的数字会飘。写进文章的数字应该用多次运行的中位数，并把区间一起写出来。
"""

import argparse
import asyncio
import statistics
import time

import ds_job_match
import jev_job_match
from job_data import load_jobs, load_resume


def _fmt(ms: float) -> str:
    return f"{ms:,.0f} ms"


def _verdict(result: dict) -> str:
    if result.get("error"):
        return "解析失败"
    return "匹配" if result.get("match") else "不匹配"


async def run_once(jobs: list[dict], resume: str) -> dict:
    """两边同时开跑，各自计时，返回一次完整结果。"""

    async def run_jev():
        start = time.perf_counter()
        outcome = await jev_job_match.match_all(jobs, resume)
        return outcome["results"], (time.perf_counter() - start) * 1000

    async def run_llm():
        start = time.perf_counter()
        results = []
        for job in jobs:
            results.append(await ds_job_match.is_match(job, resume))
        return results, (time.perf_counter() - start) * 1000

    (jev_results, jev_ms), (llm_results, llm_ms) = await asyncio.gather(run_jev(), run_llm())
    return {"jev_results": jev_results, "jev_ms": jev_ms,
            "llm_results": llm_results, "llm_ms": llm_ms}


def print_detail(jobs, outcome) -> None:
    print(f"{'岗位':<24}{'JEV':<18}{'DeepSeek':<18}{'一致'}")
    print("-" * 68)
    for jev_item, llm_item in zip(outcome["jev_results"], outcome["llm_results"]):
        if llm_item.get("error") or jev_item.get("error"):
            same = "—"
        else:
            same = "是" if jev_item["match"] == llm_item["match"] else "否"
        prob = jev_item.get("prob")
        jev_cell = f"{_verdict(jev_item)} {prob:.2f}" if prob is not None else _verdict(jev_item)
        print(f"{jev_item['title']:<24}{jev_cell:<18}{_verdict(llm_item):<18}{same}")

    total = len(jobs)
    print("-" * 68)
    print(f"{'总耗时':<24}{_fmt(outcome['jev_ms']):<18}{_fmt(outcome['llm_ms']):<18}")
    print(f"{'平均每个判断':<24}{_fmt(outcome['jev_ms'] / total):<18}{_fmt(outcome['llm_ms'] / total):<18}")

    errors = [r for r in outcome["llm_results"] if r.get("error")]
    if errors:
        print(f"\nDeepSeek 解析失败 {len(errors)} 个：")
        for item in errors:
            print(f"  · {item['title']}: {item['error']}")


def print_summary(runs: list[dict]) -> None:
    jev = [r["jev_ms"] for r in runs]
    llm = [r["llm_ms"] for r in runs]
    ratios = [r["llm_ms"] / r["jev_ms"] for r in runs]

    print(f"\n{'':<12}{'中位数':>12}{'最小':>12}{'最大':>12}")
    print("-" * 48)
    for label, values in (("JEV", jev), ("DeepSeek", llm)):
        print(f"{label:<12}{_fmt(statistics.median(values)):>12}"
              f"{_fmt(min(values)):>12}{_fmt(max(values)):>12}")
    print(f"{'倍数':<12}{statistics.median(ratios):>11.1f}×"
          f"{min(ratios):>11.1f}×{max(ratios):>11.1f}×")

    print(f"\n{len(runs)} 次运行：JEV 中位数 {_fmt(statistics.median(jev))}"
          f"，DeepSeek 中位数 {_fmt(statistics.median(llm))}"
          f"，快约 {statistics.median(ratios):.1f} 倍"
          f"（区间 {min(ratios):.1f}×–{max(ratios):.1f}×）")
    print("\n写进文章建议用中位数，并把区间一起写出来 —— 只写一个数字，读者重跑很容易对不上。")


async def main() -> None:
    parser = argparse.ArgumentParser(description="JEV vs DeepSeek 岗位匹配耗时对比")
    parser.add_argument("--repeat", type=int, default=1, help="重复运行的次数，默认 1")
    args = parser.parse_args()

    resume = load_resume()
    jobs = load_jobs()
    total = len(jobs)

    print(f"简历 {len(resume)} 字 · 岗位 {total} 个")
    print("预热中（不计入耗时）…")
    await asyncio.gather(jev_job_match.warmup(), ds_job_match.warmup())

    runs = []
    for index in range(args.repeat):
        if args.repeat > 1:
            print(f"\n===== 第 {index + 1} / {args.repeat} 次 =====")
        outcome = await run_once(jobs, resume)
        runs.append(outcome)
        if args.repeat == 1:
            print_detail(jobs, outcome)
        else:
            print(f"JEV {_fmt(outcome['jev_ms'])}   DeepSeek {_fmt(outcome['llm_ms'])}"
                  f"   快 {outcome['llm_ms'] / outcome['jev_ms']:.1f} 倍")

    if args.repeat == 1:
        outcome = runs[0]
        print(f"\nJEV 快 {outcome['llm_ms'] / outcome['jev_ms']:.1f} 倍")
    else:
        print_summary(runs)


if __name__ == "__main__":
    asyncio.run(main())
