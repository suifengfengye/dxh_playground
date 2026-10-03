import asyncio, time

async def fetch(name, delay):
    print(f"[{name}] 开始请求")
    await asyncio.sleep(delay)      # 关键：等待时把控制权交还给事件循环
    print(f"[{name}] 返回了")
    return name

async def main():
    start = time.perf_counter()
    await asyncio.gather(fetch("A", 1), fetch("B", 1))
    print(f"总耗时 {time.perf_counter() - start:.2f}s")

asyncio.run(main())
