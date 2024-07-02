import os

from openai import OpenAI

# https://docs.perplexity.ai/docs/model-cards
# https://docs.perplexity.ai/docs/pricing

YOUR_API_KEY = os.getenv("PERPLEXITY_API_KEY")
# It is recommended to use only single-turn conversations and avoid system prompts for the online LLMs (sonar-small-online and sonar-medium-online).
# can get up to date web results, probably will use this over google search
model = "sonar-medium-online"
# model = "sonar-medium-chat"
# model = "mistral-7b-instruct"

messages = [
    {
        "role": "system",
        "content": (
            "You are an artificial intelligence assistant and you need to "
            "engage in a helpful, detailed, polite conversation with a user."
        ),
    },
    {
        "role": "user",
        "content": (
            "What happened today in Iran?"
        ),
    },
]

client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

# chat completion without streaming
response = client.chat.completions.create(
    model=model,
    messages=messages,
)
print(response)

# chat completion with streaming
response_stream = client.chat.completions.create(
    model=model,
    messages=messages,
    # stream=True,
)
for response in response_stream:
    print(response)
