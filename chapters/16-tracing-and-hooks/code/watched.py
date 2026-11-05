"""The same run as blind.py, with one change: a Printer hook."""
from sales_tools import toolbox
from whitebox import Agent, Printer, load_model

QUESTION = "Which day had the most coffee revenue?"

agent = Agent(load_model(), toolbox, options={"temperature": 0}, hooks=[Printer()])
result = agent.run(QUESTION)
print("Answer:", result.answer)
print("Steps:", result.steps)
