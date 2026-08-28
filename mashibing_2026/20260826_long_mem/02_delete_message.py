from langchain.messages import AIMessage, RemoveMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig
from model_info import deepseek_model
from pprint import pp
from langgraph.types import Command

# @tool
# def tag_delete_flag(state: AgentState, runtime: ToolRuntime):
#     """
#     标记是否需要删除整个历史记录信息。
#     """
#     del state, runtime
#     print("调用 tag_delete_flag")
#     return {
#         "delete_all_message_flag": True
#     }

@tool
def tag_delete_flag(delete_msg: bool, runtime: ToolRuntime) -> dict:
    """
    标记是否需要删除整个历史记录信息。
    """
    if not delete_msg:
        return None
    print("调用 tag_delete_flag")
    updates = {
        "delete_all_message_flag": delete_msg,
        "messages": [
            ToolMessage(
                content=f"已更新删除聊天历史记录状态：{delete_msg}",
                tool_call_id=runtime.tool_call_id
            )
        ]
    }
    return Command(update=updates)

@after_model()
def delete_messages(state: AgentState, runtime: Runtime):
    delete_all_message_flag = state.get("delete_all_message_flag", False)
    print(f"delete_messages delete_all_message_flag: {delete_all_message_flag}")
    if not delete_all_message_flag:
        return None
    print("开始清空记录 - start")
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            AIMessage(content="历史记录已经删除！我们可以重新对话啦！")
        ],
        "delete_all_message_flag": False
    }

class CustomAgentState(AgentState):
    delete_all_message_flag: bool

agent = create_agent(
    model=deepseek_model,
    tools=[tag_delete_flag],
    middleware=[delete_messages],
    checkpointer=InMemorySaver(),
    state_schema=CustomAgentState
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

# print('=' * 80)
# print('invoke-1')
# response = agent.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": "请介绍一下你自己？！"
#         }
#     ]
# }, config=config)
# response["messages"][-1].pretty_print()

print('=' * 80)
print('invoke-2')
response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "我叫大小寒！请记住我的名字"
        }
    ]
}, config=config)
response["messages"][-1].pretty_print()

# print('=' * 80)
# print('invoke-3')
# response = agent.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": "为小狗写一首诗吧！"
#         }
#     ]
# }, config=config)
# response["messages"][-1].pretty_print()

# print('=' * 80)
# print('invoke-4')
# response = agent.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": "请问我叫什么名字"
#         }
#     ]
# }, config=config)
# response["messages"][-1].pretty_print()

print('=' * 80)
print('invoke-5')
response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "前面废话太多了，请清空聊天记录"
        }
    ]
}, config=config)
response["messages"][-1].pretty_print()

print('=' * 80)
print('invoke-6')
response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "请问我叫什么名字"
        }
    ]
}, config=config)
response["messages"][-1].pretty_print()

print('=' * 80)
# print(response)
pp(response)
