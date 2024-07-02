import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self):
        self._tools = {}  # Dictionary to store registered tools

    def register_tool(self, tool_name: str, func):
        """Registers a tool with its corresponding function."""
        self._tools[tool_name] = func

    def call_tool(self, tool_name: str, llm_tool_args: dict) -> str:
        """Calls the specified tool with the given arguments, handling LLM-specific mapping."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not registered.")

        tool_func = self._tools[tool_name]
        logger.debug(f"tool args {llm_tool_args}")

        return tool_func(**llm_tool_args)
