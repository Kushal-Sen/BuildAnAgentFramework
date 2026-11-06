"""Summarise the 45-turn chat once. Read the note the model wrote, then ask for the five facts."""
from library import OPTIONS
from staff_chat import FIVE_QUESTIONS, five_fact_chat
from whitebox import Agent, Retry, Summarise, load_model, total_tokens

BUDGET = 3000
FOR_SUMMARY = {"temperature": 0.2, "num_ctx": 8192}  # The chat being summarised must fit too.

model = Retry(load_model())  # Chapter 17: survive a slow reply.
messages = five_fact_chat()
print(f"Before: {len(messages)} messages, about {total_tokens(messages):,} tokens")

Summarise(model, BUDGET, FOR_SUMMARY).before_model(messages)
print(f"After:  {len(messages)} messages, about {total_tokens(messages):,} tokens")
print("The note:")
print(messages[0].content.split("Earlier in this conversation: ")[1][:500])
print()

agent = Agent(model, options=OPTIONS)
for _, question, word in FIVE_QUESTIONS:
    answer = agent.run(question, history=messages).answer
    print(f"{'pass' if word in answer.lower() else 'FAIL'}  {question}  {answer[:60]}")
