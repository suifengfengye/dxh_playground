# from dataclasses import dataclass

from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore
from langchain.tools import ToolRuntime, tool
from typing_extensions import TypedDict
from pydantic import BaseModel

from model_info import deepseek_model

# @dataclass
class Context(BaseModel):
    user_id: str

class UserInfo(TypedDict):
    username: str



store = InMemoryStore()

# 先存一点数据进去
namespace = ("dxh_123", "preferences")
store.put(namespace, "fruit", { "like": ["orange", "banana"], "dislike": ["apple"] })
store.put(namespace, "sport", { "like": ["basketball", "football"], "dislike": ["pingpong"] })
store.put(namespace, "color", { "like": ["red", "yellow"], "dislike": ["绿色"] })

@tool
def get_user_favorite_color(runtime: ToolRuntime):
    """
    获取用户最喜欢的颜色信息。
    """
    store = runtime.store
    user_id = runtime.context.user_id
    color_item = store.get((user_id, "preferences"), "color")
    if not color_item:
        return "暂无信息"
    favorite_color = color_item.value.get("like", [])

    if not favorite_color:
        return f"没有找到用户{user_id}喜欢的颜色"
    color_str = ",".join([item for item in favorite_color])

    return f"用户{user_id}喜欢的颜色为:{color_str}"

@tool
def store_user_info(user_info: UserInfo, runtime: ToolRuntime):
    """
    存储用户信息。
    Args:
        - user_info: 用户信息
    """
    store = runtime.store
    user_id = runtime.context.user_id
    store.put((user_id, "preferences"), user_id, dict(user_info))
    print("xxxx", user_id)
    return "Successfully saved user info."
    
    return f"用户{user_id}喜欢的颜色为:{color_str}"
agent = create_agent(
    model=deepseek_model,
    tools=[get_user_favorite_color, store_user_info],
    middleware=[],
    store=store,
    context_schema=Context
)

agent.invoke(
    {"messages": [{"role": "user", "content": "用户最喜欢什么颜色？！"}]},
    # user_id passed in context to identify whose information is being updated
    context=Context(user_id="dxh_123"),
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "我叫大小寒！！"}]},
    # user_id passed in context to identify whose information is being updated
    context=Context(user_id="dxh_123"),
)

# You can access the store directly to get the value
item = store.get(namespace, "dxh_123")
print(item)
