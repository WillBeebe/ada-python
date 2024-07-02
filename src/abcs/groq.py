import logging
import os

from abcs.openai import OpenAILLM
from openai import OpenAI
from tools.tool_manager import ToolManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# https://docs.cohere.com/reference/chat
class GroqLLM(OpenAILLM):
    def __init__(self, api_key: str=os.environ.get("GROQ_API_KEY"), model: str="llama3-70b-8192", tool_manager: ToolManager=None, system_prompt: str=""):
        super().__init__(api_key=api_key, model=model, tool_manager=tool_manager, system_prompt=system_prompt)
        self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
