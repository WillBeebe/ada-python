import logging

from abcs.llm import LLM
from abcs.models import PromptResponse, StreamingPromptResponse

# from metrics.main import call_tool_counter, generate_text_counter
from storage.storage_manager import StorageManager
from tools.tool_manager import ToolManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent(LLM):
    def __init__(self, client, tool_manager: ToolManager, system_prompt: str = "", tools=[], storage_manager: StorageManager = None):
        if len(tools) == 0 and (client.provider == "openai" or client.provider == "groq"):
            tools = None
        self.tools = tools
        logger.debug("Initializing Agent with tools: %s and system prompt: '%s'", tools, system_prompt)
        super().__init__(
            client=client,
            model=None,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            storage_manager=storage_manager,
        )

    def get_history(self):
        logger.debug("Fetching history")
        if self.storage_manager is not None:
            history = self.storage_manager.get_past_messages(id=id)
            logger.debug("Fetched history with %d messages", len(history))
            return history
        logger.debug("No storage manager found, returning empty history")
        return []

    async def generate_text(self, prompt: str) -> PromptResponse:
        # generate_text_counter.add(1)
        logger.debug("Generating text for prompt: '%s'", prompt)
        past_messages = []
        if self.storage_manager is not None:
            # todo: move this logic elsewhere, hacky for now
            # if self.storage_manager.get_past_messages_callback is not None:
            #     past_messages = self.storage_manager.get_past_messages_callback()
            # else:
            past_messages = await self.storage_manager.get_past_messages()
            logger.debug("Fetched %d past messages", len(past_messages))
        # todo: push down to core llm class, leave for now while scripting

        try:
            logger.debug("passing %d past messages", len(past_messages))
            if self.storage_manager is not None:
                await self.storage_manager.store_message("user", prompt)
            response = self.client.generate_text(prompt, past_messages, self.tools)
        except Exception as e:
            logger.error("Error generating text: %s", e, exc_info=True)
            if self.storage_manager is not None:
                self.storage_manager.remove_last()
            raise e

        if self.storage_manager is not None:
            try:
                # translated = self._translate_response(response)
                await self.storage_manager.store_message("assistant", response.content)
            except Exception as e:
                logger.error("Error storing messages: %s", e, exc_info=True)
                raise e

        # logger.debug("Generated response: %s", response)
        # return self._translate_response(response)
        return response

    def call_tool(self, past_messages, tool_msg, tools) -> str:
        # call_tool_counter.add(1)
        logger.debug("Calling tool with message: %s", tool_msg)
        try:
            if len(tools) == 0:
                result = self.client.call_tool(past_messages, tool_msg, self.tools)
            else:
                result = self.client.call_tool(past_messages, tool_msg, tools)
            logger.debug("Tool call successful")
            return result
        except Exception as e:
            logger.error("Error calling tool: %s", e, exc_info=True)
            raise e

    def _translate_response(self, response) -> PromptResponse:
        pass
    #     try:
    #         translated_response = self.client._translate_response(response)
    #         return translated_response
    #     except Exception as e:
    #         logger.error("Error translating response: %s", e, exc_info=True)
    #         raise e

    async def generate_text_stream(self,
                                   prompt: str,
                                   **kwargs) -> StreamingPromptResponse:
        """Generates streaming text based on the given prompt and additional arguments."""
        past_messages = []
        if self.storage_manager is not None:
            past_messages = self.storage_manager.get_past_messages()
            logger.debug("Fetched %d past messages", len(past_messages))
        if self.storage_manager is not None:
            self.storage_manager.store_message("user", prompt)
        try:
            response = await self.client.generate_text_stream(prompt, past_messages, self.tools)
        except Exception as err:
            if self.storage_manager is not None:
                self.storage_manager.remove_last()
            raise err

        # TODO: can't do this with streaming. have to handle this in the API
        # if self.storage_manager is not None:
        #     try:
        #         # translated = self._translate_response(response)
        #         self.storage_manager.store_message("assistant", response.content)
        #     except Exception as e:
        #         logger.error("Error storing messages: %s", e, exc_info=True)
        #         raise e

        return response
