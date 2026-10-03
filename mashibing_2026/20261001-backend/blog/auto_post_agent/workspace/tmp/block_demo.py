import asyncio, time

async def fetch(name, delay):
    print(f"[{name}] 开始请求")
    time.sleep(delay)               # 阻塞式睡眠：整个线程都停在这
    print(f"[{name}] 返回了")

async def main():
    start = time.perf_counter()
    await asyncio.gather(fetch("A", 1), fetch("B", 1))
    print(f"总耗时 {time.perf_counter() - start:.2f}s")

asyncio.run(main())
