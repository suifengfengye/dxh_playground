from deepagents import create_deep_agent
from deepagents.backends import StateBackend, FilesystemBackend, LocalShellBackend, CompositeBackend
from langgraph.store.memory import InMemoryStore

from llm import ds_llm

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/backend_ws": FilesystemBackend(
                root_dir="./backend_ws",
                virtual_mode=True
            ),
            "/shell_ws": LocalShellBackend(
                root_dir="./shell_ws",
                virtual_mode=True,
                env={
                    "PATH": "/opt/miniconda3/envs/langgraph-learn:/bin"
                }
            )
        }
    ),
    store=InMemoryStore()
)

