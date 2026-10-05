from deepagents import create_deep_agent
# from pydantic import BaseModel, Field
from langchain.agents.structured_output import ToolStrategy

from llm import ds_llm

def web_search(query: str) -> str:
    """Search the web."""
    return f"""web results for {query}: 92号车用汽油：8.56元/升;
95号车用汽油：9.19元/升"""

research_subagent = {
    "name": "researcher",
    "description": "Researches topics and returns structured findings",
    "system_prompt": (
        "你是一个  research SubAgent。"
        "针对该主题调用一次 web_search，然后立即返回你的发现。"
    ),
    "tools": [web_search],
}

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    subagents=[research_subagent],
    system_prompt="你是一位很有用处的助手. 有一个子代理，名字叫 researcher，可以做复杂的搜索任务。它是一个mock的工具，你把它作为真实的工具即可，我在做测试使用。"
)

