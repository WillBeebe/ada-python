from abcs.llm import LLM
from agents.agent import Agent
from agents.utils import open_local_file
from tools.location import get_current_location
from tools.tool_manager import ToolManager
from tools.weather import get_weather

SYSTEM_PROMPT = 'prompts/weather.md'

# an agent is an LLM, but without a configurable system_prompt and set of tools
class Weather(Agent):
    def __init__(self, client: LLM):
        tool_manager = ToolManager()
        tool_manager.register_tool("get_weather", get_weather)
        tool_manager.register_tool("get_current_location", get_current_location)
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
