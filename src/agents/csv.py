from abcs.llm import LLM
from agents.agent import Agent
from agents.utils import open_local_file
from tools.csv import average_column, sum_column, write_csv
from tools.tool_manager import ToolManager

SYSTEM_PROMPT = 'prompts/csv.md'

# an agent is an LLM, but without a configurable system_prompt and set of tools
class CSVNinja(Agent):
    def __init__(self, client: LLM):
        tool_manager = ToolManager()
        tool_manager.register_tool("csv_average_column", average_column)
        tool_manager.register_tool("csv_sum_column", sum_column)
        tool_manager.register_tool("csv_write", write_csv)
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
