from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[],
    checkpointer=InMemorySaver()
)

config = {"configurable": {"thread_id": "daxiaohan_01"}}

resp1 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "您好！我的名字叫张三！"
        }
    ]
}, config=config)

print(resp1)

print("-" * 100)

resp2 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "您好！请问我叫什么名字"
        }
    ]
}, config=config)

print(resp2)