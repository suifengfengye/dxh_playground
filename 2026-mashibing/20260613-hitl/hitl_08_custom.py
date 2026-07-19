from langchain_core.messages import ToolMessage

from langchain.agents import create_agent
from langchain.agents.middleware import after_model, AgentState
from langchain.tools import tool
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime

ORDERS = { 
    "ORD001": {"user": "张三", "amount": 200, "status": "已付款"},
    "ORD002": {"user": "李四", "amount": 3000, "status": "已付款"},
    "ORD003": {"user": "王五", "amount": 15000, "status": "已发货"},
}

@tool
def get_order(order_id: str) -> str:
    """
    根据订单ID获取订单信息。
    Args:
        order_id: 订单ID，如 ORD001
    Returns:
        订单信息
    """
    order = ORDERS.get(order_id, None)
    if not order:
        return f"没有查询到订单号为:{order_id}的订单"
    return (f"订单号:{order_id}, 用户:{order.get("user")}"
            f"金额:{order.get("amount")}, 状态:{order.get("status")}")

@tool
def process_refund(order_id: str):
    """
    执行退款操作。
    Args:
        order_id: 订单ID，如 ORD001
    Returns:
        退款成功消息
    """
    order = ORDERS.get(order_id, None)
    if not order:
        return f"没有查询到订单号为:{order_id}的订单，无法退款"
    return f"订单{order_id}执行退款完毕，退款金额:{order.get("amount")}"

@after_model
def human_in_the_loop(state: AgentState, runtime: Runtime) -> dict | None:
    """
    人工介入中间件。
    处理订单的退款流程。
    1. 如果订单的退款金额小于500，执行放行，无需审批。
    2. 如果订单的亏款金额大于等于500，那么发起审批。
        - 2.1 审批通过，执行退款
        - 2.2 审批拒绝，不执行退款，并返回拒绝原因。
    """
    last_message = state.get("messages", [])[-1]
    if not last_message:
        print(f"没有需要处理的执行")
        return None
    # print(f"last_message:{last_message}")
    tool_calls = last_message.tool_calls
    if not tool_calls:
        print(f"没有工具调用，不进行拦截")
        return None
    
    for tool_call in tool_calls:
        if tool_call.get("name") != "process_refund":
            # 这里 只 处理退款的工具调用
            continue
        args = tool_call.get('args', None)
        if not args:
            continue
        order_id = args.get("order_id", None)
        if not order_id:
            continue
        
        order = ORDERS.get(order_id, None)
        if not order:
            continue

        amount = order.get("amount")
        if amount < 500:
            print(f"退款金额小于500，不需要审批，执行放行")
            return None

        print(f"订单{order_id}的订单金额为:{order.get("amount")},大于500元，触发审批!")
        review_result  = interrupt({
            "action_requests": [
                {
                    "name": tool_call.get("name"),
                    "args": tool_call.get("args"),
                    "description": f"退款审批,订单:{order_id},用户:{order.get("user")},订单金额:{order.get("amount")}"
                }
            ],
            "review_configs": [
                {
                    "action_name": tool_call.get("name"),
                    "allowed_decisions": ["approve", "reject"]
                }
            ]
        })

        # 审批通过/拒绝后执行
        print(f"review_result:{review_result}")
        decision = review_result["decisions"][0]

        if decision.get("type") == 'approve':
            print(f"审批通过，放行，后续agent会执行退款操作")
            return None

        if decision.get("type") == 'reject':
            reason = decision.get("message", "退款申请被拒绝") 
            print(f" >>> 已拒绝：{reason}")
            return {
                "messages": [
                    ToolMessage(
                        content=reason, 
                        tool_call_id=tool_call["id"]
                    )
                ]
            }

    return None



agent = create_agent(
    model="ollama:qwen3:latest",
    tools=[get_order, process_refund],
    middleware=[human_in_the_loop],
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
        
        interrupted = False

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
                if chunk.get("__interrupt__", None):
                    # next_cycle_input = []
                    decisions = []
                    interrupt_list = chunk.get("__interrupt__", [])
                    for interrupt_info in interrupt_list:
                        action_requests = interrupt_info.value.get("action_requests", [])
                        review_configs = interrupt_info.value.get("review_configs", [])
                        for index, action_item in enumerate(action_requests):
                            review_item = review_configs[index]
                            print(f"\n工具 {index} 需要您的审批:{action_item.get("name", "-")},参数:{action_item.get("args", "-")}")
                            while True:
                                approval_input = input(f"请输入审批信息,{review_item.get("allowed_decisions", "-")}:").lower()
                                if approval_input == "approve":
                                    interrupted = True
                                    decisions.append({
                                        "type": "approve"
                                    })
                                    break
                                elif approval_input == 'reject':
                                    interrupted = True
                                    reason = input(f"请输入拒绝原因:")
                                    decisions.append({
                                        "type": "reject",
                                        "message": reason
                                    })
                                    break
                                else:
                                    continue

        if interrupted:
            next_input = Command(resume={
                "decisions": decisions
            })
            continue
        else:
            # 打印分行
            print("")
            print("--" * 80)
            break