"""Provided: ask a follow-up question, first without history, then with it."""
from sales_tools import toolbox
from whitebox import Agent, load_model

agent = Agent(load_model(), toolbox, options={"temperature": 0})
first = agent.run("What was the coffee revenue on Monday? The files are in the sales folder.")
print("First:  ", first.answer)
print("Without:", agent.run("And on Tuesday?").answer)
print("With:   ", agent.run("And on Tuesday?", first.messages).answer)
