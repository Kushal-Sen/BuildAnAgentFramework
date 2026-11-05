"""Provided: run the agent to the end, then read the Result."""
from sales_tools import toolbox
from whitebox import Agent, load_model

agent = Agent(load_model(), toolbox, options={"temperature": 0})
result = agent.run("What was the coffee revenue on Monday? The files are in the sales folder.")
print("Answer: ", result.answer)
print("Steps:  ", result.steps)
print("Stopped:", result.stopped)
print("Messages:", [message.role for message in result.messages])
