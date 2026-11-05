"""Run the coffee question five times, and print each answer for you to mark by eye."""
from sales_tools import toolbox
from whitebox import Agent, load_model

QUESTION = "What was the total coffee revenue across all the days in the sales folder?"

agent = Agent(load_model(), toolbox, options={"temperature": 0.7})
for run in range(1, 6):
    result = agent.run(QUESTION)
    print(f"Run {run}, {result.steps} steps: {result.answer}")
