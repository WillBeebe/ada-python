import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from abcs.llm import LLM
from abcs.models import (
    OllamaResponse,
    PromptResponse,
    StreamingPromptResponse,
    UsageStats,
)
from ollama import Client
from tools.tool_manager import ToolManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaLLM(LLM):
    def __init__(
        self,
        api_key: str = os.environ.get("NONE"),
        model: str = "llama3:8b",
        tool_manager: Optional[ToolManager] = None,
        system_prompt: str = "",
    ):
        client = Client()
        super().__init__(
            client=client,
            model=model,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            provider="ollama",
        )

    def take_tool_action(self, tool_msg: Dict[str, Any]) -> Any:
        if not self.tool_manager:
            raise ValueError("ToolManager is not set.")
        name = tool_msg.name
        arguments = tool_msg.input
        print(arguments)
        return self.tool_manager.call_tool(name, arguments)

    def generate_text(
        self,
        prompt: str,
        past_messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> PromptResponse:
      try:
          combined_history = past_messages
          combined_history.append(
              {
                  "role": "user",
                  "content": prompt,
              }
          )
          # https://github.com/ollama/ollama-python
          # client = Client(host="https://120d-2606-40-15c-13ba-00-460-7bae.ngrok-free.app",)

          # todo: generate vs chat
          # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
          response = self.client.chat(
              model=self.model,
              messages=combined_history,
              # num_predict=4000
              # todo
              # system=self.system_prompt
              )
          return self._translate_response(response)
      except Exception as e:
          logger.exception(f"An error occurred while prompting Ollama: {e}")
          raise e

    def call_tool(
        self,
        past_messages: List[Dict[str, str]],
        tool_msg: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Any:
        try:
            _ = self.take_tool_action(tool_msg)
        except Exception as e:
            logger.exception(f"Error calling tool: {e}")
            raise e
        pass

        # return response, tool_message

    def _translate_response(self, response) -> PromptResponse:
      try:
          res = OllamaResponse.model_validate(response)
          return PromptResponse(
              content=res.message.content,
              raw_response=response,
              error={},
              usage=UsageStats(
                  input_tokens= res.prompt_eval_count,
                  output_tokens= res.eval_count,
                  extra= {
                      'total_duration': res.total_duration,
                      'load_duration': res.load_duration,
                      'prompt_eval_count': res.prompt_eval_count,
                      'prompt_eval_duration': res.prompt_eval_duration,
                      'eval_count': res.eval_count,
                      'eval_duration': res.eval_duration,
                      'tokens_per_second': res.eval_count / res.eval_duration
                  }
              )
          )
      except KeyError as e:
          logger.error(f"KeyError while translating Ollama response: {e}")
          raise e
      except Exception as e:
          logger.exception(f"An error occurred while translating Ollama response: {e}")
          raise e

    async def generate_text_stream(
        self,
        prompt: str,
        past_messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> StreamingPromptResponse:
        combined_history = past_messages + [{"role": "user", "content": prompt}]

        try:
            combined_history = past_messages
            combined_history.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )
            # https://github.com/ollama/ollama-python
            # client = Client(host="https://120d-2606-40-15c-13ba-00-460-7bae.ngrok-free.app",)

            # todo: generate vs chat
            # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
            stream = self.client.chat(
                model=self.model,
                messages=combined_history,
                stream=True,
                # num_predict=4000
                # todo
                # system=self.system_prompt
                )


            async def content_generator():
                for chunk in stream:
                    if chunk['message']['content']:
                        yield chunk['message']['content']
                    # Small delay to allow for cooperative multitasking
                    await asyncio.sleep(0)

            return StreamingPromptResponse(
                content=content_generator(),
                raw_response=stream,
                error={},
                usage=UsageStats(
                    input_tokens=0,  # These will need to be updated after streaming
                    output_tokens=0,
                    extra={},
                ),
            )
        except Exception as e:
            logger.exception(f"An error occurred while streaming from Claude: {e}")
            raise e

    async def handle_tool_call(self, tool_calls, combined_history, tools):
        pass
