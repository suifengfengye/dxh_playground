# 1. 背景
AI出现之后，每年都有好几个爆火的技术和开源仓库。作为一个10-10-5的牛马，几乎没有时间关注科技的动向。

帮忙分析过去几年爆火的技术/开源仓库爆火之前的量化信息。

我知道的技术/开源仓库

1. MCP
2. A2A
3. Dify
4. RAGFlow
5. OpenClaw
请补充更多。

那这些技术在爆火之前，它在github上的数据增长曲线是怎样的（star/fork等等）

# 2. idea

想要根据1的信息，做一个监控github仓库Trend变动的小工具。帮忙设计方案。

1. 后端设计：使用python语言，看看github是否有开放API可以实现。
    每天运行一次，将监控的github仓库的star/fork/watch数据记录下来。
2. 前端：nextjs，echarts做一个简单呈现 + github仓库的简单介绍+跳转。
