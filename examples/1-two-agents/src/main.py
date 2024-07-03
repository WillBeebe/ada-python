from abcs.anthropic import AnthropicLLM
from abcs.openai import OpenAILLM
from agents.aristotle import Aristotle
from agents.plato import Plato

aristotle = Aristotle(client=AnthropicLLM())
# other agents don't have to be from other providers,
# but they can be. (todo: link)
plato = Plato(client=OpenAILLM())
chat_rounds = 3

def chat(prompt):
  for i in range(chat_rounds):
    print(f":ROUND {i} / {chat_rounds}:")
    response = aristotle.generate_text(prompt)
    prompt = response.content
    print(":Aristotle:")
    print(response.content)
    print("\n"*1)

    response = plato.generate_text(prompt)
    prompt = response.content
    print(":Plato:")
    print(response.content)
    print("\n"*1)


prompt = """I'm studying for an exam about Plato.
     I want to role play as Plato to test my knowledge.
     Can you act as Aristotle and challenge my core beliefs?
     """
print("\n"*2)
print(":USER:")
print(prompt)
print("\n"*2)
chat(prompt)



