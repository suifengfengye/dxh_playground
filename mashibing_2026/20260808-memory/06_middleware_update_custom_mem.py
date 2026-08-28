from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langchain.agents.middleware import before_model, after_model
from langgraph.runtime import Runtime

class CustomAgentState(AgentState):
    tool_call_count: int
    model_call_count: int

@tool
def get_weather():
    """查询天气预报"""
    return f"查询天气预报成功，今天天气是晴天☀️"

@tool
def get_city_info(city: str):
    """获取城市的旅游信息"""
    return f"{city}是一座旅游城市，非常适合旅游，有七星岩、象鼻山、两江四湖、阳朔等景点！"

@before_model
def handle_before_model(state: AgentState, runtime: Runtime):
    messages = state.get("messages", [])
    tool_call_count = len([msg for msg in messages if isinstance(msg, ToolMessage)])
    print(f"tool_call_count:{tool_call_count}")
    return {
        "tool_call_count": tool_call_count,
    }

@after_model
def handle_after_model(state: AgentState, runtime: Runtime):
    model_call_count = state.get("model_call_count", 0)
    print(f"model_call_count:{model_call_count}")
    return {
        "model_call_count": model_call_count + 1,
    }


agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[get_weather, get_city_info],
    middleware=[handle_before_model, handle_after_model],
    checkpointer=InMemorySaver(),
    state_schema=CustomAgentState
)

config = {"configurable": {"thread_id": "daxiaohan_01"}}

resp1 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "桂林适合旅游吗？明天过去可以吗，天气允许么？"
        }
    ]
}, config=config)

print(resp1)
