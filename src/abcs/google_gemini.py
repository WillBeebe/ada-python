import logging
from typing import Any, Dict, List, Optional

import google.ai.generativelanguage as glm
import google.generativeai as genai
from abcs.llm import LLM
from abcs.models import PromptResponse, UsageStats
from tools.tool_manager import ToolManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiLLM(LLM):
    def __init__(
        self,
        api_key: str,
        model: str,
        tool_manager: Optional[ToolManager] = None,
        system_prompt: Optional[str] = None,
    ):
        genai.configure(api_key=api_key)
        client = genai.GenerativeModel(model)
        super().__init__(
            client=client,
            model=model,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            provider="google",
        )

    def take_tool_action(self, tool_msg: Dict[str, Any]) -> Any:
        if not self.tool_manager:
            raise ValueError("ToolManager is not set.")
        name = tool_msg.function_call.name
        arguments = tool_msg.function_call.args
        return self.tool_manager.call_tool(name, arguments)

    def generate_text(
        self,
        prompt: str,
        past_messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> PromptResponse:
        try:
            combined_history = []
            if self.system_prompt:
                combined_history.append({"role": "user", "parts": [self.system_prompt]})
                combined_history.append({"role": "model", "parts": ["okie dokie"]})
            for msg in past_messages:
                combined_history.append(
                    {
                        "role": "model" if msg["role"] == "assistant" else msg["role"],
                        "parts": [msg["content"]],
                    }
                )
            combined_history.append({"role": "user", "parts": [prompt]})
            # all_parts = ["".join(msg["parts"]) for msg in combined_history]

            # todo: this is only an estimate of tokens
            # token_client = genai.GenerativeModel('gemini-pro')
            # input_tokens = token_client.count_tokens(contents=''.join(all_parts)).total_tokens
            # output_tokens += token_client.count_tokens(contents=response.text).total_tokens


            tool_obj = {
                    "function_declarations": tools
                }
            logger.info(tool_obj)
            response = self.client.generate_content(
                combined_history,
                tools=tool_obj,
            )
            logger.info(response)
            selected_msg = response.candidates[0]

            logger.info("selected")
            logger.info(selected_msg)
            logger.info(selected_msg.content.parts[0].function_call)

            if selected_msg.content.parts[0].function_call:
                tool_msg = selected_msg.content.parts[0]
                response = self.call_tool(
                    combined_history + [{"role": "model", "parts": selected_msg.content.parts}],
                    tool_msg,
                    tools=tools,
                )
                # do we need to count these?
                # output_tokens += token_client.count_tokens(contents=response.text).total_tokens

            return self._translate_response(response)
        except Exception as e:
            logger.exception(f"An error occurred while prompting Gemini: {e}")
            raise e

    def call_tool(
        self,
        past_messages: List[Dict[str, Any]],
        tool_msg: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        try:
            action_response = self.take_tool_action(tool_msg)
        except Exception as e:
            logger.exception(f"Error calling tool: {e}")
            raise e

        client = genai.GenerativeModel(self.model)
        tool_obj = {
                    "function_declarations": tools
                }
        logger.info(tool_obj)
        response = client.generate_content(
            past_messages + [
                glm.Content(
                    parts=[
                        glm.Part(
                            function_response=glm.FunctionResponse(
                                name=tool_msg.function_call.name,
                                response={"result": action_response},
                            )
                        )
                    ]
                ),
            ],
            tools=tool_obj,
        )

        return response

    def _translate_response(
        self,
        response,
        input_tokens: int = 0,
        output_tokens: int = 0
    ) -> PromptResponse:
        try:
            return PromptResponse(
                content=response.candidates[0].content.parts[0].text,
                raw_response=response,
                error={},
                usage=UsageStats(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    extra={},
                ),
            )
        except Exception as e:
            logger.exception(f"An error occurred while translating response: {e}")
            raise e
