

from abcs.llm import LLM
from agents.agent import Agent
from storage.memory_storage import MemoryStorage
from tools.tool_manager import ToolManager


class Base(Agent):
    def __init__(self, client: LLM, storage_manager: any = None):
        tool_manager = ToolManager()
        # override client tool manager
        client.tool_manager = tool_manager
        tools = client.load_tool_definitions()

        storage = storage_manager
        if storage_manager is None:
            storage = MemoryStorage()
        client.storage_manager = storage_manager

        super().__init__(
            client=client,
            tool_manager=tool_manager,
            tools=tools,
            storage_manager=storage,
        )
