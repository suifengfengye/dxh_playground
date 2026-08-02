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

agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[],
    middleware=[
        # Redact emails in user input before sending to model
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
        ),
        # Mask credit cards in user input
        PIIMiddleware(
            "credit_card",
            strategy="mask",
            apply_to_input=True,
        ),
        # Block API keys - raise error if detected
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="hash", # hash | block(抛出异常)
            apply_to_input=True,
            apply_to_output=True,
        ),
        handle_before_agent,
        handle_before_model,
        handle_wrap_tool_call,
        handle_wrap_model_call,
        handle_after_model,
        handle_after_agent,
    ]
)

result = agent.invoke({
        "messages": [
            # {
            #     "role": "user",
            #     "content": "请拉取 1527161981@qq.com 的邮件列表！"
            # },
            # {
            #     "role": "user",
            #     "content": "4111111111111111 这个信用卡的额度是你每个月可以花费的token金额！"
            # },
            {
                "role": "user",
                "content": "我的API_Key为:sk-7096d73804b24r6u7b17bef928e2f1e2,为什么一直调不通deepseek的API呢？我搞错了吗？"
            },
        ]
    }
)

print(result)