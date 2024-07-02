from abcs.llm import LLM
from agents.agent import Agent
from agents.utils import open_local_file
from tools.tool_manager import ToolManager

SYSTEM_PROMPT = 'prompts/people/descartes.md'

class Descartes(Agent):
    def __init__(self, client: LLM):
        tool_manager = ToolManager()
        # override client tool manager
        client.tool_manager = tool_manager
        tools = client.load_tool_definitions()
        system_prompt = open_local_file(SYSTEM_PROMPT)
        super().__init__(
            client=client,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            tools=tools,
        )
