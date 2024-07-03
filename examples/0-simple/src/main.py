from abcs.anthropic import AnthropicLLM
from agents.ada import Ada

agent = Ada(client=AnthropicLLM())

def chat(prompt):
  print(":USER:")
  print(prompt)
  print("\n"*3)
  response = agent.generate_text(prompt)
  print(":ADA:")
  print(response.content)
  print("\n"*3)

print("\n"*2)
chat("Name five fruit that start with the letter a.")
# Ada has a few tools, this is one of them (todo: link)
chat("Get the repo structure of the current directory.")
# agents store history in-memory by default,
# they can be configured to work with other storage backends like postgres, mongo, etc...
chat("Summarize our conversation in 10 words.")


