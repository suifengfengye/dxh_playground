import asyncio, warnings

async def hello():
    print("这行只有在被 await 时才会执行")
    return 1

coro = hello()          # 注意：没有任何输出
print("hello() 只是造出了一个协程对象:", coro)
coro.close()
