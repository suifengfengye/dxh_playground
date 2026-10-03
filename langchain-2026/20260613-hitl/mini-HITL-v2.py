import argparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from enum import Enum
from datetime import datetime
import zoneinfo
import json
from pathlib import Path

# 时区固定东八区（深圳）
TZ = zoneinfo.ZoneInfo("Asia/Shanghai")

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
class InterruptStatusEnum(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    WAITING_HUMAN = "WAITING_HUMAN"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RESUMING = "RESUMING"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"

@dataclass
class Interrupt():
    id: int
    status: InterruptStatusEnum
    action_name: str
    action_args: Dict[str, Any]
    allowed_decisions: List[str]
    created_time: datetime
    updated_time: datetime

    def to_json(self) -> str:
        data = asdict(self)
        # 枚举转字符串
        data["status"] = data["status"].value
        # datetime转带时区ISO标准字符串
        data["created_time"] = data["created_time"].isoformat()
        data["updated_time"] = data["updated_time"].isoformat() if data["updated_time"] else None
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "Interrupt":
        raw = json.loads(json_str)
        raw["status"] = InterruptStatusEnum(raw["status"])
        # ISO字符串转回datetime，自动识别时区
        raw["created_time"] = datetime.fromisoformat(raw["created_time"])
        raw["updated_time"] = datetime.fromisoformat(raw["updated_time"]) if raw["updated_time"] else None
        return cls(**raw)

STORE_PATH = Path("store.txt")

# 通用读写函数不变
def save_interrupt_list(items: List[Interrupt]):
    STORE_PATH.write_text("\n".join([i.to_json() for i in items]), encoding="utf-8")

def load_interrupt_list() -> List[Interrupt]:
    if not STORE_PATH.exists():
        return []
    lines = [l.strip() for l in STORE_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [Interrupt.from_json(line) for line in lines]

def get_interrupt_by_id(interrupt_id: str) -> Interrupt:
    interrupt_list = load_interrupt_list()
    for item in interrupt_list:
        if item.id == interrupt_id:
            return item
    return None

def get_latest_iterrupt() -> Interrupt:
    interrupt_list = load_interrupt_list()
    if not interrupt_list:
        return {"latest_id": 0, "latest_interrupt": None}
    latest_interrupt = interrupt_list[0]
    latest_id = latest_interrupt.id
    for item in interrupt_list:
        cur_id = item.id
        if cur_id > latest_id:
            latest_id = cur_id
            latest_interrupt = item
    
    # return (latest_id, latest_interrupt)
    return {"latest_id": latest_id, "latest_interrupt": latest_interrupt}

def append_interrupt(item: Interrupt):
    with open(STORE_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + item.to_json())

def create_interrupt_task(order_id: str):
    interrupt_info = get_latest_iterrupt()
    max_interrupt_id = interrupt_info.get("latest_id")

    interrupt = Interrupt(
        id=max_interrupt_id + 1,
        status=InterruptStatusEnum.WAITING_HUMAN,
        action_name="process_refund",
        action_args={
            "order_id": order_id
        },
        allowed_decisions=["approve", "reject"],
        created_time=datetime.now(tz=TZ),
        updated_time=None
    )
    append_interrupt(interrupt)
    return (interrupt)


def agent_refund(order_id: str):
    order = ORDERS.get(order_id, None)
    if not order:
        print(f"没有查询到订单,订单ID:{order_id}")
        return
    if order["amount"] <= 500:
        refund_result = process_refund(order_id)
        print(refund_result)
        return
    
    # 订单金额大于 500
    # 创建一个 interrupt_task , 做持久化处理
    (interrupt) = create_interrupt_task(order_id)
    print(f"订单金额大于500元，需要审批,审批单ID:{interrupt.id}。订单ID:{order_id},用户:{order.get("user")}, 金额:{order.get("amount")}。"
    f"可执行 python mini-HITL-v2.py approve|reject {interrupt.id} [拒绝原因] 命令进行审批。")

def agent_interrupt_list():
    interrrupt_list = load_interrupt_list()
    for interrupt_item in interrrupt_list:
        print(f"ID:{interrupt_item.id},状态:{interrupt_item.status},action_name:{interrupt_item.action_name},"
        f"action_args:{interrupt_item.action_args},"
        f"更新时间:{interrupt_item.updated_time},"
        f"创建时间:{interrupt_item.created_time}。")

def agent_decision(decision: str, interrupt_id: int, reject_reason: str = None):
    interrupt_list = load_interrupt_list()
    interrupt = None
    for item in interrupt_list:
        if item.id == interrupt_id:
            interrupt = item
    if not interrupt:
        print(f"没有找到{interrupt_id}对应的审批单!")
        return
    
    if interrupt.status != InterruptStatusEnum.WAITING_HUMAN:
        print(f"审批单状态为:{interrupt.status},是已完成状态，不能进行审批！")
        return

    if decision == "approve":
        if interrupt.action_name == "process_refund":
            action_args = interrupt.action_args
            refund_result =process_refund(**action_args)
            print(refund_result)

        interrupt.status = InterruptStatusEnum.APPROVED
    elif decision == "reject":
        interrupt.status = InterruptStatusEnum.REJECTED
        print(f"审批拒绝，原因:{reject_reason}")

    interrupt.updated_time = datetime.now(tz=TZ)
    save_interrupt_list(interrupt_list)

    


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
    parser_reject.add_argument("reject_reason", help="拒绝原因")

    args = parser.parse_args()

    print(args.command)
    # print(args.interrupt_id)
    # print(args.reject_reason)

    # 命令列表
    # python mini-HITL-v2.py start ORD001
    # python mini-HITL-v2.py list
    # python mini-HITL-v2.py approve 1
    # python mini-HITL-v2.py reject 1

    if args.command == "start":
        agent_refund(args.order_id)

    if args.command == "list":
        agent_interrupt_list()

    if args.command == "approve":
        interrupt_id = int(args.interrupt_id)
        agent_decision("approve", interrupt_id)

    if args.command == "reject":
        interrupt_id = int(args.interrupt_id)
        agent_decision("reject", interrupt_id, args.reject_reason)

if __name__ == "__main__":
    main()