from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from langgraph.checkpoint.memory import InMemorySaver

from llm import ds_llm

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    backend=StateBackend(),
    checkpointer=InMemorySaver()
)

