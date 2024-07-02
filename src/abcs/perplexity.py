import logging

from abcs.openai import OpenAILLM
from openai import OpenAI
from tools.tool_manager import ToolManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerplexityLLM(OpenAILLM):
    def __init__(self, api_key: str, model: str, tool_manager: ToolManager=None, system_prompt: str=""):
        super().__init__(api_key=api_key, model=model, tool_manager=tool_manager, system_prompt=system_prompt)
        self.client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
