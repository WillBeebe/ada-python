from abcs.llm import LLM
from agents.agent import Agent
from agents.utils import open_local_file
from storage.memory_storage import MemoryStorage
from tools.files import repo_read_all_files
from tools.tool_manager import ToolManager

SYSTEM_PROMPT = 'prompts/engineers/reviewer.md'

class EngineerReviewer(Agent):
    def __init__(self, client: LLM):
        tool_manager = ToolManager()
        tool_manager.register_tool("repo_read_all_files", repo_read_all_files)
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
