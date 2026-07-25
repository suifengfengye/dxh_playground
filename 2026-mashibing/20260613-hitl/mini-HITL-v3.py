from dataclasses import dataclass, asdict
from datetime import datetime
import zoneinfo
from pathlib import Path
from enum import Enum
import argparse
import uuid
import json

# 时区固定东八区（深圳）
TZ = zoneinfo.ZoneInfo("Asia/Shanghai")

STORE_PATH = Path("store_v3.json")

ORDERS = { 
    "ORD001": {"user": "张三", "amount": 200, "status": "已付款"},
    "ORD002": {"user": "李四", "amount": 3000, "status": "已付款"},
    "ORD003": {"user": "王五", "amount": 15000, "status": "已发货"},
}

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

# 中断状态枚举
class RunStatus(str, Enum):
    RUNNING = "RUNNING"
    WAITING_HUMAN = "WAITING_HUMAN"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

"""
状态机定义，使用 TRANSITION 转换表控制，保证状态的可控性。
"""
TRANSITIONS = {
    (RunStatus.WAITING_HUMAN, "approve"): RunStatus.APPROVED,
    (RunStatus.WAITING_HUMAN, "reject"): RunStatus.REJECTED,
    (RunStatus.APPROVED, "complete"): RunStatus.COMPLETED,
    (RunStatus.RUNNING, "auto"): RunStatus.COMPLETED,
}

def transition(cur_status: RunStatus, decision: str) -> RunStatus:
    next_status = TRANSITIONS.get((cur_status, decision))
    if not next_status:
        raise ValueError(f"非法状态迁移: {current} --{event}--> ?")
    return next_status

@dataclass
class Action:
    name: str
    args: dict


@dataclass
class RunState:
    run_id: str
    interrupt_id: str | None
    status: str
    context: dict | None
    action: dict | None
    result: str | None
    decision_message: str | None
    created_at: datetime
    updated_at: datetime

def date_now() -> datetime:
    return datetime.now(tz=TZ)

"""
持久化处理，保持一致性，简单处理。
1. 全部load
2. 全部save
"""
def get_run_dict(run: RunState) -> dict:
    run_dict = asdict(run)
    run_dict["created_at"] = run.created_at.isoformat()
    run_dict["updated_at"] = run.created_at.isoformat() if run.created_at else None
    return run_dict

def get_run_args(run_dict: dict) -> dict:
    run_dict["created_at"] = datetime.fromisoformat(run_dict["created_at"])
    run_dict["updated_at"] = datetime.fromisoformat(run_dict["updated_at"]) if run_dict["created_at"] else None
    return run_dict

def load_runs() -> list[RunState]:
    if not STORE_PATH.exists():
        return []
    data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    return [RunState(**get_run_args(item)) for item in data]

def save_runs(runs: list[RunState]) -> None:
    data_str = json.dumps([get_run_dict(run_item) for run_item in runs], ensure_ascii=False, indent=2)
    STORE_PATH.write_text(data_str, encoding="utf-8")

"""
由 action 驱动执行，而不是写死！
"""
def execute_action(action: dict):
    registry = {"process_refund": process_refund, "get_order": get_order}
    func = registry.get(action.get("name"), None)
    if not func:
        raise ValueError(f"未知 action: {action.get("name")}, args:{action.get("args")}")
    return func(**action.get("args"))

# start开始执行
def start(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        print(f"找不到对应的订单，订单id:{order_id}")
        return
    
    runs = load_runs()
    # [TODO] 应该交给LLM决策，这里没有接入，先写死
    action = Action("process_refund", { "order_id": order_id })
    run_inst = RunState(
        run_id=uuid.uuid4().hex[:8],
        interrupt_id=None,
        status=RunStatus.RUNNING.value,
        context={"order_id": order_id},
        action=asdict(action),
        result=None,
        decision_message=None,
        created_at=date_now(),
        updated_at=None
    )

    if order.get("amount") <= 500:
        print(f"订单小于或者等于500，无需审批，直接退款!")
        action_result = execute_action(run_inst.action)
        run_inst.result = action_result
        # [TODO] 没有 事物 处理
        # run_inst.status = RunStatus.COMPLETED
        next_status = transition(run_inst.status, "auto")
        run_inst.status = next_status
        print(action_result)
        runs.append(run_inst)
        save_runs(runs)
        return
    

    run_inst.interrupt_id = f"INT-{uuid.uuid4().hex[:6]}"
    run_inst.status = RunStatus.WAITING_HUMAN.value
    run_inst.updated_at = date_now()
    runs.append(run_inst)
    save_runs(runs)
    print(f"已暂停，等待人工审批。interrupt_id={run_inst.interrupt_id} order_id={order_id}")
    
# list 执行
def list_runs() -> None:
    for run in load_runs():
        print(
            f"run_id={run.run_id} interrupt_id={run.interrupt_id} "
            f"status={run.status} context={run.context} result={run.result}"
        )

# 审批执行
def review(decision: str, interrupt_id: str, message: str | None = None) -> None:
    runs = load_runs()
    run = next((item for item in runs if item.interrupt_id == interrupt_id), None)
    if not run:
        print(f"没有找到对应的审批单,interrupt_id:{interrupt_id}")
        return
    
    current = RunStatus(run.status)
    if current != RunStatus.WAITING_HUMAN:
        print(f"当前状态为 {run.status}，不能审批")
        return

    run.status = transition(cur_status=run.status, decision=decision).value

    if decision == "approve":
        action_result = execute_action(run.action)
        run.result = action_result
        run.status = transition(RunStatus.APPROVED, "complete").value
    else:
        run.result = f"审批拒绝: {message or '未提供原因'}"

    save_runs(runs)
    print(run.result)


def main():
    parser = argparse.ArgumentParser(description="Agent命令行处理工具")
    
    # 子命令：list / start / approve / reject
    # command.list / command.start / command.approve / command.reject
    subparsers = parser.add_subparsers(dest="command", required=True)

    # start order_id 命令
    parser_start = subparsers.add_parser("start", help="启动退款程序")
    parser_start.add_argument("order_id", help="审批单ID")

    # list 命令
    parser_list = subparsers.add_parser("list", help="列出Agent实例列表")

    # approve interrupt_id 命令
    parser_approve = subparsers.add_parser("approve", help="审批通过")
    parser_approve.add_argument("interrupt_id", help="中断ID")

    # reject interrupt_id 拒绝原因 命令
    parser_reject = subparsers.add_parser("reject", help="审批拒绝")
    parser_reject.add_argument("interrupt_id", help="中断ID")
    parser_reject.add_argument("message", help="拒绝原因")

    args = parser.parse_args()

    print(args.command)
    # print(args.interrupt_id)
    # print(args.reject_reason)

    # 命令列表
    # python mini-HITL-v3.py start ORD001
    # python mini-HITL-v3.py list
    # python mini-HITL-v3.py approve 1
    # python mini-HITL-v3.py reject 1

    if args.command == "start":
        start(args.order_id)

    if args.command == "list":
        list_runs()

    if args.command == "approve":
        review("approve", args.interrupt_id)

    if args.command == "reject":
        review("reject", args.interrupt_id, args.message)

if __name__ == "__main__":
    main()