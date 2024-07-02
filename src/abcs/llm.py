import os
import sys
from abc import ABC, abstractmethod
from importlib import resources

import yaml
from abcs.models import PromptResponse
from abcs.tools import gen_anthropic, gen_cohere, gen_google, gen_openai

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

class LLM(ABC):
    def __init__(self, client, model, tool_manager, system_prompt: str, provider: str= "", storage_manager: any=None):
        self.client = client
        self.model = model
        self.tool_manager = tool_manager
        self.system_prompt = system_prompt
        # todo: fix needing this in two places
        self.client.system_prompt = system_prompt
        self.provider = provider
        self.storage_manager = storage_manager

        with resources.open_text("data", "tools.yaml") as file:
            self.tool_data = yaml.safe_load(file)


    @abstractmethod
    def generate_text(self,
                      # this being a string is limiting
                      prompt: str, past_messages, tools, **kwargs) -> PromptResponse:
        """Generates text based on the given prompt and additional arguments."""
        pass

    @abstractmethod
    def call_tool(self, past_messages, tool_msg) -> str:
        """Calls a specific tool with the given arguments and returns the response."""
        pass

    @abstractmethod
    def _translate_response(self, response) -> PromptResponse:
        """Translates the provider response to a common interface"""
        pass

    def store_message(self, tool_msg) -> str:
        """Stores a message."""

    def load_tool_definitions(self):
        tool_definitions = []

        if self.provider == "":
            return tool_definitions
        for tool_name in self.tool_manager._tools:
            for tool in self.tool_data:
                if tool["name"] == tool_name:
                    if self.provider == "anthropic":
                        tool_definitions.append(gen_anthropic(tool))
                    elif self.provider == "cohere":
                        tool_definitions.append(gen_cohere(tool))
                    elif self.provider == "groq" or self.provider == "openai" or self.provider == "perplexity":
                        tool_definitions.append(gen_openai(tool))
                    elif self.provider == "google":
                        tool_definitions.append(gen_google(tool))
                    elif self.provider == "ollama":
                        pass
                    else:
                        raise('unrecognized provider')
        return tool_definitions
