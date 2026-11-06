"""Trim a 43-turn chat to a budget. Look at what's left, then ask."""
from library import OPTIONS
from staff_chat import staff_chat
from whitebox import Agent, Message, Trim, load_model, total_tokens

BUDGET = 3000
QUESTION = "What's my staff number?"

messages = staff_chat(40) + [Message("user", QUESTION)]
print(f"Before: {len(messages)} messages, about {total_tokens(messages):,} tokens")

Trim(BUDGET).before_model(messages)
print(f"After:  {len(messages)} messages, about {total_tokens(messages):,} tokens")
print("First:", messages[0].content[:60])
print("Then: ", messages[1].content[:60])

agent = Agent(load_model(), options=OPTIONS, hooks=[Trim(BUDGET)])
result = agent.run(QUESTION, history=staff_chat(40))
print("tokens_in:", result.messages[-1].tokens_in)
print("Answer:", result.answer)
