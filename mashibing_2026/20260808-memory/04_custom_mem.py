import asyncio
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver

class CustomAgentState(AgentState):
    user_id: str
    preferences: dict

async def main():
    agent = create_agent(
        model="ollama:qwen3:latest",
        tools=[],
        state_schema=CustomAgentState,
        checkpointer=InMemorySaver()
    )

    config = {"configurable": {"thread_id": "daxiaohan_01"}}

    result = agent.astream({
        "messages": [
                {
                    "role": "user",
                    "content": "您好！我的名字叫张三！"
                }
        ],
        "user_id": "daxiaohan_01",
        "preferences": {
            "hobby": "旅游、看书、搞钱!"
        }
    }, 
    stream_mode="messages",
    config=config)

    # async for item in result:
    #     print(item, end="")
    async for message, metadata in result:
        # print(message.content, end="", flush=True)
        print(message)
        print(metadata)
        print('-' * 20)

asyncio.run(main())