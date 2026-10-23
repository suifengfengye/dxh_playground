"""
自定义数据结构。
包含运行时上下文、用户偏好等定义。
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProcurementContext:
    """
    运行时上下文，在invoke/stream处传入。
    用于传递当前用户身份等基础信息。
    """
    user_id: str # 用户ID
    username: str # 用户名/登陆名

@dataclass
class UserPreferences:
    f"""
    用户偏好数据结构，存储在长期记忆文件中。
    对应 /memories/{user_id}/preferences.md 的内容 
    """
    perferred_output: Optional[str] = None # "table" | "chart"，喜欢用表还是图分析结果
    perferred_chart_type: Optional[str] = None # "bar" | "line" | "pie"
    perferred_currency: Optional[str] = None # 币种，"CNY" | "USD"
    perferred_language: Optional[str] = None # "zh" | "en"

    current_suppliers: list[str] = [] # 近期使用的供应商列表
    current_queries: list[str] = [] # 近期分析需求摘要列表

    def __post__init__(self):
        if self.current_suppliers is None:
            self.current_suppliers = []
        if self.current_queries is None:
            self.current_queries = []