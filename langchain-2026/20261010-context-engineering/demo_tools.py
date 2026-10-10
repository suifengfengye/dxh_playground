"""
演示用 tool 集合（原子操作）。

与 skill 的分工：
- tool  = 「能做什么」——原子、确定、有输入输出（如对比、算优惠）。
- skill = 「怎么做」——多步骤流程与经验，放在 skills/ 目录的 SKILL.md。

注意：尺码推荐与场合搭配已改为 skill（skills/size-guide、skills/outfit-styling），
故此处不再提供同名 tool，避免与技能重叠导致路由混乱。
"""

from langchain.tools import tool

# 演示用商品目录（真实项目里来自商品中心，而非硬编码）
CATALOG = {
    "浅灰针织连衣裙": {"price": 299, "sizes": ["S", "M", "L"], "stock": "现货充足",
                 "review": "版型显瘦，微透，建议内搭吊带"},
    "牛仔直筒长裤": {"price": 349, "sizes": ["25", "26", "27", "28", "29", "30"],
                "stock": "现货充足，支持免费改裤长", "review": "裤长偏长，160cm 需要裁边"},
    "白色短款小西装": {"price": 459, "sizes": ["S", "M"], "stock": "库存仅剩 M 码",
                 "review": "容易粘毛，适合搭配连衣裙"},
    "休闲帆布鞋": {"price": 199, "sizes": ["35", "36", "37", "38", "39", "40"],
                "stock": "现货充足", "review": "偏大半码，脚宽建议选小一码"},
}


def _find(name: str):
    """按名称做包含匹配，返回 (全名, 信息)。"""
    for full_name, info in CATALOG.items():
        if name in full_name or full_name in name:
            return full_name, info
    return None, None


@tool
def compare_products(product_a: str, product_b: str) -> str:
    """对比两件商品的价格、尺码、现货情况与评价要点。

    仅当用户明确要比较两件（或以上）商品时调用；只问单件商品时请改用 search_product。
    """
    name_a, info_a = _find(product_a)
    name_b, info_b = _find(product_b)
    if not info_a or not info_b:
        missing = product_a if not info_a else product_b
        return f"商品库里没有找到「{missing}」，无法对比。"

    def line(name, info):
        return (
            f"- {name}：{info['price']} 元 | 尺码 {','.join(info['sizes'])} | "
            f"{info['stock']} | 评价：{info['review']}"
        )

    cheaper = name_a if info_a["price"] <= info_b["price"] else name_b
    return "对比结果：\n" + line(name_a, info_a) + "\n" + line(name_b, info_b) + f"\n价格更低：{cheaper}"


@tool
def promotion_advisor(cart_total: int) -> str:
    """根据购物车金额给出可用的优惠信息。

    当用户询问「有没有优惠 / 满减 / 优惠券 / 能便宜多少」时调用。
    需要用户给出金额；用户只是在看单品价格时不要调用。
    """
    if cart_total < 0:
        return "金额看起来不对，方便再报一下购物车总价吗？"

    rules = [(500, "满 500 减 50"), (300, "满 300 减 20"), (199, "满 199 免运费")]
    hit = [text for threshold, text in rules if cart_total >= threshold]
    if not hit:
        return f"当前 {cart_total} 元暂无可用优惠，再买 {199 - cart_total} 元即可享免运费。"
    return f"购物车 {cart_total} 元，可用优惠：{'；'.join(hit)}。（演示规则）"


# 统一导出，方便在 context_agent.py 里一次性注册
DEMO_TOOLS = [compare_products, promotion_advisor]
