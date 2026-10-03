import re
from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware, before_agent, after_agent, AgentState, before_model, after_model, wrap_tool_call, wrap_model_call, ModelRequest, ModelResponse
from langgraph.runtime import Runtime
from langchain.messages import ToolMessage
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

def detect_cn_phone(content: str) -> list[dict]:
    matches = []
    pattern = r"(?<!\d)1[3-9]\d{9}(?!\d)"

    for match in re.finditer(pattern, content):
        matches.append({
            "text": match.group(0),   # 匹配到的原文
            "start": match.start(),   # 起始位置
            "end": match.end(),       # 结束位置
        })

    return matches

agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[],
    middleware=[
        PIIMiddleware(
            pii_type="cn_phone",
            detector=detect_cn_phone,
            strategy="mask",
            apply_to_input=True,
        ),
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
            "content": "我的手机号是13812345678，请帮我查询订单状态"
        }
    ]
})