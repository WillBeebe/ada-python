from abcs.anthropic import AnthropicLLM
from agents.ada import Ada

agent = Ada(client=AnthropicLLM())
prompt = "Name five fruit that start with the letter a."

print(prompt)
response = agent.generate_text(prompt)
print(response.content)
