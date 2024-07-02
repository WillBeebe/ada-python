from ada.abcs import AnthropicLLM
from ada.agents import Ada

agent = Ada(client=AnthropicLLM())
response = agent.generate_text("Name five fruit that start with the letter a.")
print(response.content)
