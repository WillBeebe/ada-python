import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import anthropic
from abcs.llm import LLM
from abcs.models import PromptResponse, StreamingPromptResponse, UsageStats
from tools.tool_manager import ToolManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnthropicLLM(LLM):
    def __init__(
        self,
        api_key: str = os.environ.get("ANTHROPIC_API_KEY"),
        model: str = 'claude-3-5-sonnet-20240620',
        # model: str = "claude-3-opus-20240229",
        # model: str = "claude-3-haiku-20240307",
        tool_manager: Optional[ToolManager] = None,
        system_prompt: str = "",
    ):
        client = anthropic.Client(api_key=api_key)
        super().__init__(
            client=client,
            model=model,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            provider="anthropic",
        )

    def take_tool_action(self, tool_msg: Dict[str, Any]) -> Any:
        if not self.tool_manager:
            raise ValueError("ToolManager is not set.")
        name = tool_msg.name
        arguments = tool_msg.input
        logger.debug(arguments)
        return self.tool_manager.call_tool(name, arguments)

    def generate_text(
        self,
        prompt: str,
        past_messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> PromptResponse:
        combined_history = past_messages + [{"role": "user", "content": prompt}]
        logger.debug(combined_history)

        try:
            response = self.client.messages.create(
                model=self.model,
                # [models](https://docs.anthropic.com/claude/docs/models-overview) for details.
                max_tokens=4096,
                messages=combined_history,
                system=self.system_prompt,
                tools=tools,
            )

            total_times = 0
            if response.stop_reason == "tool_use":
                tool_msg = None
                while response.stop_reason == "tool_use":
                    total_times += 1
                    logger.debug(f"total tool use: {total_times}")
                    # tool_msg = next((msg for msg in response.content if msg.type == "tool_use"), None)
                    # can't rely on this long-term
                    for msg in response.content:
                        if msg.type == "tool_use":
                            tool_msg = msg
                            break
                    total_history = combined_history + [{"role": response.role, "content": response.content}]
                    response, tool_message = self.call_tool(
                        total_history,
                        tool_msg,
                        tools,
                    )
                    combined_history = total_history + [tool_message]
            return self._translate_response(response)
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise e
        except Exception as e:
            logger.exception(f"An error occurred while prompting Claude: {e}")
            raise e

    def call_tool(
        self,
        past_messages: List[Dict[str, str]],
        tool_msg: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Any:
        try:
            action_response = self.take_tool_action(tool_msg)
        except Exception as e:
            logger.exception(f"Error calling tool: {e}")
            raise e

        tool_message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_msg.id,
                            "content": action_response,
                        }
                    ],
                }
        logger.debug("\n"*20)
        logger.debug(f"{past_messages + [tool_message]}")
        logger.debug("\n"*20)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.system_prompt,
            messages=past_messages + [
                tool_message
            ],
            tools=tools,
        )
        return response, tool_message

    def _translate_response(self, response) -> PromptResponse:
        try:
            content = ""
            if isinstance(response, str):
                logger.error(f"response is a string {response}")
            else:
                if len(response.content) > 0:
                    content = response.content[0].text
            return PromptResponse(
                content=content,
                raw_response=response,
                error={},
                usage=UsageStats(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    extra={},
                ),
            )
        except Exception as e:
            logger.exception(f"error: {e}\nresponse: {response}")
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
            stream = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=combined_history,
                system=self.system_prompt,
                stream=True,
            )

            async def content_generator():
                for event in stream:
                    if isinstance(event, anthropic.types.MessageStartEvent):
                        # Message start event, we can ignore this
                        pass
                    elif isinstance(event, anthropic.types.ContentBlockStartEvent):
                        # Content block start event, we can ignore this
                        pass
                    elif isinstance(event, anthropic.types.ContentBlockDeltaEvent):
                        # This is the event that contains the actual text
                        if event.delta.text:
                            yield event.delta.text
                    elif isinstance(event, anthropic.types.ContentBlockStopEvent):
                        # Content block stop event, we can ignore this
                        pass
                    elif isinstance(event, anthropic.types.MessageStopEvent):
                        # Message stop event, we can ignore this
                        pass
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
        # This is a placeholder for handling tool calls in streaming context
        # You'll need to implement the logic to execute the tool call and generate a response
        pass
