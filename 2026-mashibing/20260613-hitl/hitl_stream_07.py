from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver


@tool
def send_broadcast(msg: str):
    """发送全员广播"""
    return f"已经发送全员广播，内容为:{msg}"

@tool
def send_email(msg: str):
    """给特定人员发送邮件"""
    return f"发送邮件成功，内容为:{msg}"

@tool
def search_weather():
    """查询天气预报"""
    return f"查询天气预报成功，今天天气是晴天☀️"

agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[send_broadcast, send_email, search_weather],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_broadcast": {
                    "allowed_decisions": ["approve", "reject"]
                },
                "send_email": {
                    "allowed_decisions": ["approve", "reject"]
                },
                "delete_user": False
            }
        )
    ],
    checkpointer=InMemorySaver()
)

    # stream_mode=["messages", "updates"],

config = {"configurable": {"thread_id": "session_01"}}

# 对话轮次死循环
while True:
    user_input = input("用户:").strip()

    if user_input.lower() in ("exit", "quit", "q", "退出"):
        print("已退出，再见！")
        break

    if not user_input:
        continue

    next_input = {"messages": [{"role": "user", "content": user_input}]}

    # agent ReAct循环 
    while True:
        print("Agent:", end="")
        for type, chunk in agent.stream(
            input=next_input,
            stream_mode=["messages", "updates"],
            config=config
        ):
            # print(type, chunk)
            if type == "messages":
                message_chunk, metadata = chunk
                print(message_chunk.content, end="")
            elif type == "updates":
                # tool_calls = chunk["tool_calls"] or []
                # print("tool_calls")
                print(f"updates:{chunk}")
                


