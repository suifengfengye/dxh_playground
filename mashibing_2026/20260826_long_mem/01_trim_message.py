from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig

@before_model
def trim_messages(state: AgentState, runtime: Runtime):
    del runtime
    messages = state.get("messages", [])
    if len(messages) <= 4:
        return None

    # 保留系统消息和第一条用户自我介绍，再附加最近两条消息。
    pinned_messages = messages[:2]
    latest_messages = messages[-2:]

    kept_messages = []
    seen_ids = set()
    for message in [*pinned_messages, *latest_messages]:
        message_id = getattr(message, "id", None)
        if message_id in seen_ids:
            continue
        if message_id is not None:
            seen_ids.add(message_id)
        kept_messages.append(message)

    if len(kept_messages) == len(messages):
        return None

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *kept_messages
        ]
    }

agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[],
    middleware=[trim_messages],
    checkpointer=InMemorySaver(),
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}
print("invoke 1")
response = agent.invoke({
    "messages": [
        {
            "role": "system",
            "content": "你是一个博学多才的Agent助手，加油干！！！"
        },
        {
            "role": "user",
            "content": "hello，my name is DXH! Nice to meet you."
        }
    ]
}, config=config)
response["messages"][-1].pretty_print()

print("invoke 2")
response = agent.invoke({"messages": [{"role": "user", "content": "write a short poem for cat!"}]}, config=config)
response["messages"][-1].pretty_print()

print("invoke 3")
response = agent.invoke({"messages": [{"role": "user", "content": "Now do the same but for dog!"}]}, config=config)
response["messages"][-1].pretty_print()

print("invoke 4")
response = agent.invoke({"messages": [{"role": "user", "content": "Please summarize both poems in one sentence."}]}, config=config)
response["messages"][-1].pretty_print()

print("invoke 5")
final_response = agent.invoke({"messages": [{"role": "user", "content": "What is my Name?"}]}, config=config)
final_response["messages"][-1].pretty_print()
