"""Ask the agent a question, and see only the result."""
from sales_tools import toolbox
from whitebox import Agent, load_model

QUESTION = "Which day had the most coffee revenue?"

agent = Agent(load_model(), toolbox, options={"temperature": 0})
result = agent.run(QUESTION)
print("Answer:", result.answer)
print("Steps:", result.steps)
