from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

from llm import ds_llm

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    backend=LocalShellBackend(
        root_dir="./backend_ws",
        virtual_mode=True,
        env={
            "PATH": "/opt/miniconda3/envs/langgraph-learn/bin:/bin"
        }
    )
)

