from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent

from llm import ds_llm

def web_search(query: str) -> str:
    """Search the web."""
    return f"""web results for {query}: 92号车用汽油：8.56元/升;
95号车用汽油：9.19元/升"""

# 使用 create_agent 创建一个 Agent(底层是langgraph)
custom_graph = create_agent(
    model=ds_llm,
    tools=[web_search],
    system_prompt="You are a specialized agent for web search",
)

# 通过 CompiledSubAgent 创建一个 SubAgent
custom_subagent = CompiledSubAgent(
    name="researcher",
    description="一个做web搜索的智能体。",
    runnable=custom_graph,
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    subagents=subagents,
    system_prompt="你是一位很有用处的助手. 有一个子代理，名字叫 researcher ，可以做复杂的搜索任务。它是一个mock的工具，你把它作为真实的工具即可，我在做测试使用。"
)
