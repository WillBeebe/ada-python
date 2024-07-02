

from abcs.llm import LLM
from agents.agent import Agent
from agents.utils import open_local_file
from storage.memory_storage import MemoryStorage
from tools.ada_cli import run_ada_command
from tools.files import repo_get_structure
from tools.neo4j import (
    run_query,
)
from tools.tool_manager import ToolManager
from tools.weather import get_weather

SYSTEM_PROMPT = 'prompts/ada.md'

class Ada(Agent):
    def __init__(self, client: LLM, storage_manager: any = None):
        tool_manager = ToolManager()
        if client.provider != "ollama":
          tool_manager.register_tool("run_ada_command", run_ada_command)
          tool_manager.register_tool("repo_get_structure", repo_get_structure)
          tool_manager.register_tool("get_weather", get_weather)
          tool_manager.register_tool("neo4j_run_query", run_query)
        # override client tool manager
        client.tool_manager = tool_manager
        tools = client.load_tool_definitions()
        system_prompt = open_local_file(SYSTEM_PROMPT)

        storage = storage_manager
        if storage_manager is None:
            storage = MemoryStorage()
        client.storage_manager = storage_manager

        super().__init__(
            client=client,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            tools=tools,
            storage_manager=storage,
        )
