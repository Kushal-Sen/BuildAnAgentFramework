"""Provided: every safety net on, a harder question, five runs. usage: python3 still_wrong.py"""
import re

from sales_tools import toolbox
from whitebox import Agent, LoopGuard, RescueToolCalls, Retry, load_model

QUESTION = "How much more was made from coffee than from tea across all the days in the sales folder?"

model = Retry(RescueToolCalls(load_model()))
agent = Agent(model, toolbox, options={"temperature": 0.7}, hooks=[LoopGuard()])
right = 0
for run in range(1, 6):
    result = agent.run(QUESTION)
    results = [message.content for message in result.messages if message.role == "tool"]
    errors = sum(text.startswith("Error: ") for text in results)
    right += "135" in result.answer
    numbers = re.findall(r"\d+", result.answer) or ["none"]
    print(f"Run {run}: {errors} tool errors. The last number in the answer: {numbers[-1]}")
print(f"Reached 135: {right}/5")
