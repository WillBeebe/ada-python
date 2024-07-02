from abcs.llm import LLM
from agents.agent import Agent
from agents.utils import open_local_file
from storage.memory_storage import MemoryStorage
from tools.files import file_write, repo_get_structure
from tools.tool_manager import ToolManager

SYSTEM_PROMPT = 'prompts/engineers/coordinator.md'

class EngineerCoordinator(Agent):
    def __init__(self, client: LLM, task_function):
        tool_manager = ToolManager()
        tool_manager.register_tool("repo_get_structure", repo_get_structure)
        # tool_manager.register_tool("file_write", file_write)
        tool_manager.register_tool("agent_assign_task", task_function)
        storage_manager = MemoryStorage()
        # override client tool manager
        client.tool_manager = tool_manager
        client.storage_manager = storage_manager
        tools = client.load_tool_definitions()
        system_prompt = open_local_file(SYSTEM_PROMPT)
        super().__init__(
            client=client,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            tools=tools,
            storage_manager=storage_manager,
        )