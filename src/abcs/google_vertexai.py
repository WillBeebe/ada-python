import logging
from typing import Any, Dict, List, Optional

import vertexai
from abcs.llm import LLM
from abcs.models import PromptResponse, UsageStats
from tools.tool_manager import ToolManager
from vertexai.generative_models import (
    Content,
    # FunctionDeclaration,
    GenerativeModel,
    Part,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# work in progress
# https://cloud.google.com/vertex-ai/generative-ai/docs/prompt-gallery/samples/chat_animal_facts_8
class VertexAILLM(LLM):
    def __init__(
        self,
        api_key: str,
        project: str,
        location: str,
        model: str,
        tool_manager: Optional[ToolManager] = None,
        system_prompt: str = "",
        # tools_file: str = "./src/tools.json",
    ):
        # Initialize Vertex AI and the client
        vertexai.init(project=project, location=location)
        client = GenerativeModel(model)
        super().__init__(
            client=client,
            model=model,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            provider="vertexai",
        )

    def take_tool_action(self, tool_msg: Dict[str, Any]) -> Any:
        if not self.tool_manager:
            raise ValueError("ToolManager is not set.")
        name = tool_msg['function_call']['name']
        arguments = tool_msg['function_call']['args']

        return self.tool_manager.call_tool(name, arguments)

    def generate_text(
        self,
        prompt: str,
        past_messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> PromptResponse:
        combined_history = [
            Content(
                role="assistant" if msg["role"] == "assistant" else "user",
                parts=[Part.from_text(msg["content"])],
            )
            for msg in past_messages
        ]
        if self.system_prompt:
            combined_history.insert(
                0,
                Content(
                    role="system",
                    parts=[Part.from_text(self.system_prompt)],
                )
            )
        combined_history.append(
            Content(
                role="user",
                parts=[Part.from_text(prompt)],
            )
        )

        try:
            response = self.client.generate_content(
                combined_history,
                tools=[self.weather_tool],
            )
            logger.debug('before tool use')
            logger.debug(response)

            selected_msg = response.candidates[0]
            if selected_msg.finish_reason == 1 and selected_msg.content.parts[0].function_call:
                tool_msg = selected_msg.content.parts[0]
                response = self.call_tool(
                    combined_history + [Content(role="assistant", parts=selected_msg.content.parts)],
                    tool_msg,
                    tools
                )

            return self._translate_response(response)
        except Exception as e:
            logger.exception(f"An error occurred while prompting Vertex AI: {e}")
            raise e

    def call_tool(
        self,
        past_messages: List[Dict[str, Any]],
        tool_msg: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> PromptResponse:
        try:
            action_response = self.take_tool_action(tool_msg)
        except Exception as e:
            logger.exception(f"Error calling tool: {e}")
            raise e

        response = self.client.generate_content(
            past_messages + [
                Content(
                    parts=[
                        Part.from_function_response(
                            name="get_current_weather",
                            response={"content": action_response},
                        )
                    ]
                ),
            ],
            tools=tools,
        )

        return self.translate_response(response)

    def _translate_response(self, response) -> PromptResponse:
        try:
            selected_msg = response.candidates[0]
            return PromptResponse(
                content=selected_msg.content.parts[0].text,
                raw_response=response,
                error={},
                usage=UsageStats(
                    input_tokens=response.usage['input_tokens'],
                    output_tokens=response.usage['output_tokens'],
                    extra={},
                ),
            )
        except Exception as e:
            logger.exception(f"An error occurred while translating Vertex AI response: {e}")
            raise e
