import json
import logging
import os
from typing import Any, Dict, List, Optional

import openai_multi_tool_use_parallel_patch  # type: ignore  # noqa: F401
from abcs.llm import LLM
from abcs.models import PromptResponse, UsageStats
from openai import OpenAI
from tools.tool_manager import ToolManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolResponse:
    def __init__(self, role: str, content: str, content_raw: object):
        self.role = role
        self.content = content
        self.content_raw = content_raw

class OpenAILLM(LLM):
    def __init__(
        self,
        api_key: str = os.environ.get("OPENAI_API_KEY"),
        model: str = "gpt-4o",
        tool_manager: Optional[ToolManager] = None,
        system_prompt: str = "",
    ):
        client = OpenAI(api_key=api_key)
        logger.info("Initializing OpenAI LLM with model: '%s' and system prompt: '%s'", model, system_prompt)
        super().__init__(
            client=client,
            model=model,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            provider="openai",
        )

    def take_tool_action(self, tool_msg: Dict[str, Any]) -> Any:
        if not self.tool_manager:
            logger.error("ToolManager is not set.")
            raise ValueError("ToolManager is not set.")
        name = tool_msg.function.name
        arguments = json.loads(tool_msg.function.arguments)
        logger.debug("Taking tool action with name: %s and arguments: %s", name, arguments)
        try:
            result = self.tool_manager.call_tool(name, arguments)
            logger.info("Tool action successful")
            return result
        except Exception as e:
            logger.error("Error in tool action: %s", e, exc_info=True)
            raise e

    def generate_text(
        self,
        prompt: str,
        past_messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> PromptResponse:
        system_message = [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []
        combined_history = system_message + past_messages + [{"role": "user", "content": prompt}]
        logger.debug("Generating text with prompt: '%s'", prompt)

        try:
            logger.debug('\n'*10)
            logger.debug(combined_history)
            logger.debug('\n'*10)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=combined_history,
                tools=tools,
            )
            choice = response.choices[0]
            logger.info("Generated response successfully")

            total_tool_calls = 0
            if choice.message.tool_calls:
                if self.storage_manager is not None:
                        raw_content = {}
                        raw_content['role'] = choice.message.role
                        raw_content['content'] = choice.message.content
                        tool_calls = []
                        for tool in choice.message.tool_calls:
                            tool_calls.append({
                                "id": tool.id,
                                "type": tool.type,
                                "function": {
                                    "arguments": tool.function.arguments,
                                    "name": tool.function.name
                                }
                            })
                        raw_content['tool_calls'] = tool_calls
                        logger.debug(choice.message)
                        logger.debug(raw_content)
                        msg = ToolResponse(role=choice.message.role,content=choice.message.content,content_raw=raw_content)
                        self.storage_manager.store_raw(msg)
                # for openai all tool calls need to be done first, before any messages are stored
                # todo: update call_tool method with this logic
                all_history = combined_history + [choice.message]
                for tool_msg in choice.message.tool_calls:
                    total_tool_calls += 1
                    logger.debug('\n'*10)
                    logger.debug(all_history)
                    logger.debug('\n'*10)
                    action_response = self.take_tool_action(tool_msg)
                    tool_response_message = {
                        "role": "tool",
                        "content": action_response,
                        "tool_call_id": tool_msg.id,
                    }
                    if self.storage_manager is not None:
                        msg = ToolResponse(role=tool_response_message['role'],content=tool_response_message['content'],content_raw=tool_response_message)
                        self.storage_manager.store_raw(msg)
                    all_history.append(tool_response_message)

                logger.info(f"post tool calls, number of calls: {total_tool_calls}")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=all_history,
                    # might be able to remove
                    # tools=tools,
                )
            return self._translate_response(response)
        except Exception as e:
            logger.error("Error generating text: %s", e, exc_info=True)
            raise e

    # not currently used, needs to be refactored with the logic above remove the completions call
    def call_tool(
        self,
        past_messages: List[Dict[str, str]],
        tool_msg: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        logger.debug("Calling tool with message: %s", tool_msg)
        try:
            action_response = self.take_tool_action(tool_msg)
        except Exception as e:
            logger.error("Error calling tool: %s", e, exc_info=True)
            raise e

        # system_message = [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []
        try:
            logger.info(f"tool msg {tool_msg}")
            tool_response_message = {
                        "role": "tool",
                        "content": action_response,
                        "tool_call_id": tool_msg.id,
                    }
            all_messages = past_messages + [
                    tool_response_message
                ]
            logger.debug(f"calling tool completion {tool_response_message}")
            logger.debug(f"calling tool completion {all_messages}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                # might be able to remove
                tools=tools,
            )
            logger.info("Tool call successful")
            return response, tool_response_message
        except Exception as e:
            logger.error("Error during tool response creation: %s", e, exc_info=True)
            raise e

    def _translate_response(self, response) -> PromptResponse:
        try:
            content = response.choices[0].message.content
            if content is None:
                content = "done"
            return PromptResponse(
                content=content,
                raw_response=response,
                error={},
                usage=UsageStats(
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    extra={},
                ),
            )
        except Exception as e:
            # check what exec_info is
            # logger.error("An error occurred while translating OpenAI response: %s", e, exc_info=True)
            logger.exception(f"error: {e}\nresponse: {response}")
            raise e
