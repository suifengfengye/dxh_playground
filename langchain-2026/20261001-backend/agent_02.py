from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from llm import ds_llm

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    backend=FilesystemBackend(
        root_dir="./backend_ws",
        virtual_mode=True
    )
)

