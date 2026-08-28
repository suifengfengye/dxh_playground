from tkinter import NO

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


@after_model
def custom_summarize_middleware(state: AgentState, runtime: Runtime):
    """
    自定义总结摘要中间件。
    保留最近N条信息，对更早之前的信息进行摘要总结。
    """
    threshold = 5
    max_retain = 2
    messages = state.get("messages", [])

    if len(messages) < threshold:
        return None
    
    retain_messages = messages[-max_retain:]
    summarize_messages = messages[:-max_retain]

    # 如果保留的最后一条信息是 ToolMessage 需要往前找到一条不是 ToolMessage的信息，避免上下文丢失
    if isinstance(retain_messages[0], ToolMessage):
        # append_messages = []
        count = 0
        for item_msg in reversed(summarize_messages):
            retain_messages.insert(0, item_msg)
            count += 1
            if not isinstance(item_msg, ToolMessage):
                break
        summarize_messages = summarize_messages[:-count]

    if not summarize_messages:
        return None

    system_prompt = f"""请对下面的内容进行总结：
    {summarize_messages}
    """

    result_msg = deepseek_model.invoke(system_prompt)

    retain_messages = [result_msg] + retain_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *retain_messages
        ]
    }


agent = create_agent(
    model=deepseek_model,
    tools=[get_market_info],
    middleware=[
        print_before_model, 
        print_after_model,
        custom_summarize_middleware,
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

