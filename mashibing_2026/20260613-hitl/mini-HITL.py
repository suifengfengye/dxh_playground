def action():
    ...

def hitl():
    ...


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

def main():
    print("HITL Demo")
    while True:
        order_id = input("请输入订单ID:")
        order = ORDERS.get(order_id)
        if not order:
            print("没有查询到对应订单")
            continue
        amount = order.get("amount")
        if amount < 500:
            print(f"订单金额小于500，无需审批。:{order_id},用户:{order.get("user")},订单金额:{order.get("amount")}")
            continue

        if amount >= 500:
            print(f"订单金额大于等于500，触发审批。:{order_id},用户:{order.get("user")},订单金额:{order.get("amount")}")
            while True:
                # TODO 这里如何设计中断和恢复执行
                decision = input("请审批,[approve, reject]:").lower()
                if decision == 'approve':
                    print(f"审批通过")
                    print("-" * 100)
                    break
                if decision == 'reject':
                    print(f"审批拒绝❌！")
                    print("-" * 100)
                    break
                print(f"输入的审批信息不对，请继续输入。")

if __name__ == "__main__":
    main()