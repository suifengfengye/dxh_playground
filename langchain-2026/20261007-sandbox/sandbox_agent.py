from dotenv import dotenv_values

from deepagents import create_deep_agent

from daytona import Daytona, DaytonaConfig
from langchain_daytona import DaytonaSandbox

from llm import ds_llm

env_config = dotenv_values(".env")

config = DaytonaConfig(
    api_key=env_config["DAYTONA_API_KEY"],
    target="us"
)
sandbox = Daytona(config).create()
backend = DaytonaSandbox(sandbox=sandbox)

agent = create_deep_agent(
    model=ds_llm,
    tools=[],
    backend=backend
)

