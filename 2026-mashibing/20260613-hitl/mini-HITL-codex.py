import argparse
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


ORDERS = {
    "ORD001": {"user": "张三", "amount": 200, "status": "已付款"},
    "ORD002": {"user": "李四", "amount": 3000, "status": "已付款"},
    "ORD003": {"user": "王五", "amount": 15000, "status": "已发货"},
}
STORE_PATH = Path(__file__).with_name("mini_hitl_codex_store.json")


class RunStatus(str, Enum):
    RUNNING = "RUNNING"
    WAITING_HUMAN = "WAITING_HUMAN"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


TRANSITIONS = {
    (RunStatus.WAITING_HUMAN, "approve"): RunStatus.APPROVED,
    (RunStatus.WAITING_HUMAN, "reject"): RunStatus.REJECTED,
    (RunStatus.APPROVED, "complete"): RunStatus.COMPLETED,
}


@dataclass
class Action:
    name: str
    args: dict


@dataclass
class RunState:
    run_id: str
    interrupt_id: str | None
    order_id: str
    status: str
    action: dict | None
    result: str | None
    decision_message: str | None
    created_at: str
    updated_at: str


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_runs() -> list[RunState]:
    if not STORE_PATH.exists():
        return []
    data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    return [RunState(**item) for item in data]


def save_runs(runs: list[RunState]) -> None:
    STORE_PATH.write_text(
        json.dumps([asdict(run) for run in runs], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def transition(current: RunStatus, event: str) -> RunStatus:
    next_status = TRANSITIONS.get((current, event))
    if not next_status:
        raise ValueError(f"非法状态迁移: {current} --{event}--> ?")
    return next_status


def process_refund(order_id: str) -> str:
    order = ORDERS.get(order_id)
    if not order:
        return f"未找到订单 {order_id}，无法退款"
    return f"订单 {order_id} 退款成功，金额 {order['amount']} 元"


def execute_action(action: dict) -> str:
    registry = {"process_refund": process_refund}
    func = registry.get(action["name"])
    if not func:
        raise ValueError(f"未知 action: {action['name']}")
    return func(**action["args"])


def start(order_id: str) -> None:
    order = ORDERS.get(order_id)
    if not order:
        print(f"未找到订单 {order_id}")
        return
    runs = load_runs()
    action = Action(name="process_refund", args={"order_id": order_id})
    run = RunState(
        run_id=uuid.uuid4().hex[:8],
        interrupt_id=None,
        order_id=order_id,
        status=RunStatus.RUNNING.value,
        action=asdict(action),
        result=None,
        decision_message=None,
        created_at=now(),
        updated_at=now(),
    )
    if order["amount"] < 500:
        run.result = execute_action(run.action)
        run.status = RunStatus.COMPLETED.value
        runs.append(run)
        save_runs(runs)
        print(run.result)
        return

    run.interrupt_id = f"INT-{uuid.uuid4().hex[:6]}"
    run.status = RunStatus.WAITING_HUMAN.value
    run.updated_at = now()
    runs.append(run)
    save_runs(runs)
    print(f"已暂停，等待人工审批。interrupt_id={run.interrupt_id} order_id={order_id}")


def list_runs() -> None:
    for run in load_runs():
        print(
            f"run_id={run.run_id} interrupt_id={run.interrupt_id} "
            f"status={run.status} order_id={run.order_id} result={run.result}"
        )


def review(interrupt_id: str, decision: str, message: str | None = None) -> None:
    runs = load_runs()
    run = next((item for item in runs if item.interrupt_id == interrupt_id), None)
    if not run:
        print(f"未找到 interrupt_id={interrupt_id}")
        return
    current = RunStatus(run.status)
    if current != RunStatus.WAITING_HUMAN:
        print(f"当前状态为 {run.status}，不能审批")
        return

    run.status = transition(current, decision).value
    run.decision_message = message
    run.updated_at = now()
    if decision == "approve":
        run.result = execute_action(run.action)
        run.status = transition(RunStatus.APPROVED, "complete").value
    else:
        run.result = f"审批拒绝: {message or '未提供原因'}"
    save_runs(runs)
    print(run.result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini HITL Demo")
    sub = parser.add_subparsers(dest="command", required=True)
    p_start = sub.add_parser("start")
    p_start.add_argument("order_id")
    sub.add_parser("list")
    p_review = sub.add_parser("review")
    p_review.add_argument("interrupt_id")
    p_review.add_argument("decision", choices=["approve", "reject"])
    p_review.add_argument("message", nargs="?")
    args = parser.parse_args()

    if args.command == "start":
        start(args.order_id)
    elif args.command == "list":
        list_runs()
    else:
        review(args.interrupt_id, args.decision, args.message)


if __name__ == "__main__":
    main()
