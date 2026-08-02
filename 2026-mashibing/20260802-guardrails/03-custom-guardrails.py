import re
from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import before_agent, after_agent, AgentState, before_model, after_model, wrap_tool_call, wrap_model_call, ModelRequest, ModelResponse
from langgraph.runtime import Runtime
from langchain.messages import AIMessage, ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langgraph.types import Command

@before_agent
def handle_before_agent(state: AgentState, runtime: Runtime):
    latest_message = state.get("messages", [])[-1]
    if not latest_message:
        return
    print(f"before_agent:{latest_message.content}")
    print("-" * 100)

@after_agent
def handle_after_agent(state: AgentState, runtime: Runtime):
    latest_message = state.get("messages", [])[-1]
    if not latest_message:
        return
    print(f"after_agent:{latest_message.content}")
    print("-" * 100)

@before_model
def handle_before_model(state: AgentState, runtime: Runtime):
    latest_message = state.get("messages", [])[-1]
    if not latest_message:
        return
    print(f"before_model:{latest_message.content}")
    print("-" * 100)

@after_model
def handle_after_model(state: AgentState, runtime: Runtime):
    latest_message = state.get("messages", [])[-1]
    if not latest_message:
        return
    print(f"after_model:{latest_message.content}")
    print("-" * 100)

@wrap_tool_call
def handle_wrap_tool_call(request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    print(f"Executing tool: {request.tool_call['name']}")
    print(f"Arguments: {request.tool_call['args']}")

    result = handler(request)
    print("Tool completed successfully")
    return result

@wrap_model_call
def handle_wrap_model_call(request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],):
    latest_message = request.messages[-1]
    if not latest_message:
        return handler(request)
    print(f"wrap_model_call:{latest_message.content}")
    print("-" * 100)
    return handler(request)


forbidden_list = [
    "暴力",
    "血腥",
    "自残",
    "自杀",
    "毒品",
    "诈骗",
    "洗钱",
    "赌博",
    "仇恨",
    "歧视",
    "色情",
    "恐怖主义",
    "爆炸物",
    "枪支",
    "黑客",
    "盗号",
    "木马",
    "勒索软件",
]

@before_agent(can_jump_to=["end"])
def custom_guardrail(state: AgentState, runtime: Runtime):
    messages = state.get("messages", [])
    latest_message = messages[-1] if messages else None
    if not latest_message:
        return None

    content = latest_message.content
    if not isinstance(content, str):
        content = str(content)

    matched_words = [word for word in forbidden_list if word in content]
    if not matched_words:
        return None

    return {
        "jump_to": "end",
        "messages": [
            AIMessage(
                content=(
                    "检测到输入中包含敏感或违规词汇，已阻止本次请求。"
                    f"命中词语: {', '.join(matched_words)}"
                )
            )
        ],
    }

agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[],
    middleware=[
        custom_guardrail,
        handle_before_agent,
        handle_before_model,
        handle_wrap_tool_call,
        handle_wrap_model_call,
        handle_after_model,
        handle_after_agent,
    ],
)

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "帮我写一篇暴力美学的电影剧本！控制在200字以内！"
        }
    ]
})
