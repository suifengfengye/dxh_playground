from langchain.messages import AIMessage, RemoveMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model, before_model
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig
from model_info import deepseek_model
from pprint import pp
from langgraph.types import Command
from langchain.agents.middleware import SummarizationMiddleware

@tool
def get_market_info() -> dict:
    """
    获取股市大盘信息。
    """
    return f"今天股市大盘涨停！！！再也没见过这么好的牛市了！"

@before_model()
def print_before_model(state: AgentState, runtime: Runtime):
    """
    调用模型前打印信息。
    """
    messages = state.get("messages", [])
    print("before_model:")
    pp(messages)

@after_model()
def print_after_model(state: AgentState, runtime: Runtime):
    """
    调用模型后打印信息。
    """
    messages = state.get("messages", [])
    print("after_model:")
    pp(messages)


agent = create_agent(
    model=deepseek_model,
    tools=[get_market_info],
    middleware=[
        print_before_model, 
        print_after_model,
        SummarizationMiddleware( 
            model=deepseek_model, 
            trigger=('messages',5), # 当消息数量超过5条时触发总结 
            keep=('messages', 2), # 保留最后2条消息 
        )
    ],
    checkpointer=InMemorySaver(),
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "请问你是谁？！"
        }
    ]
}, config=config)
agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "我叫大小寒！请记住我的名字"
        }
    ]
}, config=config)

agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "今天股市大盘怎么样啦？"
        }
    ]
}, config=config)

agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "如果能活100岁，人会多难受呀？"
        }
    ]
}, config=config)

agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "好了！天黑请闭眼！"
        }
    ]
}, config=config)

