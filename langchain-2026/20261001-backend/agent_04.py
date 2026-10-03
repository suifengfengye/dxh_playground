from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

from llm import ds_llm

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    backend=StoreBackend(
        namespace=lambda rt: (f"{rt.execution_info.thread_id}",),
    ),
    store=InMemoryStore()
)

