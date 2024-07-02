import logging

import cohere
from abcs.llm import LLM
from abcs.models import PromptResponse, UsageStats
from tools.tool_manager import ToolManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# https://docs.cohere.com/reference/chat
class CohereLLM(LLM):
    def __init__(
        self, api_key: str, model: str, tool_manager: ToolManager = None, system_prompt: str = ""
    ):
        client = cohere.Client(api_key=api_key)
        super().__init__(
            client=client,
            model=model,
            tool_manager=tool_manager,
            system_prompt=system_prompt,
            provider="cohere"
        )

    def take_tool_action(self, tool_msg):
        name = tool_msg.name
        arguments = tool_msg.parameters
        return self.tool_manager.call_tool(name, arguments)

    def generate_text(self, prompt: str, past_messages, tools, **kwargs) -> PromptResponse:
        try:
            combined_history = []
            for msg in past_messages:
              combined_history.append({
                  "role": 'CHATBOT' if msg['role'] == 'assistant' else 'USER',
                  "message": msg['content'],
              })
            response = self.client.chat(
              chat_history=combined_history,
              message=prompt,
              tools=tools,
              model=self.model,
              # perform web search before answering the question. You can also use your own custom connector.
              # connectors=[{"id": "web-search"}],
            )
            logger.debug('before tool use')
            logger.debug(response)

            if response.tool_calls is not None and len(response.tool_calls) > 0:
                tool_msg = response.tool_calls[0]
                response = self.call_tool(
                    combined_history
                    + [{"role": "CHATBOT", "content": response.text}],
                    tool_msg,
                    tools,
                )
            logger.debug('after tool use')
            logger.debug(response)

            return self._translate_response(response)
        except Exception as e:
            logger.exception(f"An error occurred while prompting Cohere: {e}")
            raise e

    # https://docs.cohere.com/docs/tool-use
    def call_tool(self, past_messages, tool_msg, tools) -> str:
        action_response = self.take_tool_action(tool_msg)
        logger.debug(action_response)
        logger.debug(tool_msg)
        tool_results = [{
            "call": {
                "name": tool_msg.name,
                "parameters": tool_msg.parameters,
                # TODO: add this to the tool_msg
                "generation_id": "1234"
            },
            "outputs": [
                {
                    # TODO: read tool-use docs to sort this out
                    "date": "1234",
                    "summary": action_response
                }
            ]
        }]

        response = self.client.chat(
            # other models have to be coaxed to show their chain of thought
            model=self.model,
            # Different models have different maximum values for this parameter. See
            # [models](https://docs.anthropic.com/claude/docs/models-overview) for details.
            # max_tokens=4096,
            # system=self.system_prompt,
            # temperature=0.1,
            # todo: should this be the previous prompt?
            message="hello",
            tools=tools,
            tool_results=tool_results
        )
        return response

    # todo: write tests for all of these translate reponse methods
    def _translate_response(self, response) -> PromptResponse:
        logger.debug(response.chat_history)
        logger.debug(response.meta.billed_units)
        model_response = response.chat_history[len(response.chat_history) - 1]
        try:
            return PromptResponse(
                content=model_response.message,
                raw_response=response,
                error={},
                usage=UsageStats(
                    input_tokens=response.meta.billed_units.input_tokens,
                    output_tokens=response.meta.billed_units.output_tokens,
                    extra={},
                ),
            )
        # todo: should we return an empty PromptResponse from here too? feels like it
        except Exception as e:
            logger.exception(
                f"An error occurred while translating Claude response: {e}"
            )
            raise e

