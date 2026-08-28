import asyncio
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain_core.messages import ToolMessage

class CustomAgentState(AgentState):
    user_id: str
    level: str
    preferences: dict

@tool
def get_user_info(runtime: ToolRuntime):
    """
    获取用户信息。
    Args:
        runtime: 运行时实例对象
    """
    # print(f"@tool runtime:{runtime}")

    user_id = runtime.state["user_id"]
    level = runtime.state["level"]
    preferences = runtime.state["preferences"]

    return f"用户ID:{user_id}, 用户等级:{level}, 用户偏好:{preferences}"

@tool
def update_user_info(runtime: ToolRuntime, user_id: str, level: str, preferences: dict):
    """
    修改用户信息:
    Args:
        runtime: 工具运行时实例
        user_id: 用户ID
        level：用户等级
        preferences:用户偏好
    """
    print(f"update_user_info:{user_id}, {level}, {preferences}")
    if not user_id or not level or not preferences:
        return Command(update={
            "messages": [ToolMessage(
                    content="没有对应的用户信息",
                    tool_call_id= runtime.tool_call_id
                )
            ]
        })

    return Command(update={
            "messages": [ToolMessage(
                    content = "用户信息已经更新啦!!!!->大小寒_02",
                    tool_call_id = runtime.tool_call_id
                )],
            "user_id": "大小寒_02",
            "level": "NORMAL",
            "preferences": {
                "hobby": "自媒体、写代码！!"
            }
        })
    

async def main():
    agent = create_agent(
        model="ollama:qwen3:latest",
        tools=[get_user_info, update_user_info],
        state_schema=CustomAgentState,
        checkpointer=InMemorySaver()
    )

    config = {"configurable": {"thread_id": "daxiaohan_01"}}

    result = agent.invoke({
        "messages": [
                {
                    "role": "user",
                    "content": "我的用户信息是什么？"
                }
        ],
        "user_id": "daxiaohan_01",
        "level": "VIP",
        "preferences": {
            "hobby": "旅游、看书、搞钱!"
        }
    },
    config=config)

    print(result)

    result = agent.invoke({
        "messages": [
                {
                    "role": "user",
                    "content": ("帮我修改用户信息,用户ID:大小寒_02,用户等级:NORMAL,用户偏好：自媒体、写代码！!")
                }
        ],
        "user_id": "daxiaohan_01",
        "level": "VIP",
        "preferences": {
            "hobby": "旅游、看书、搞钱!"
        }
    },
    config=config)
    print(result["messages"][-1].content)

asyncio.run(main())