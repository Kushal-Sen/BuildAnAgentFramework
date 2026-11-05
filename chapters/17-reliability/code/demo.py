"""Run the sales agent with every safety net. usage: python3 demo.py [provider/name]"""
import sys

from sales_tools import toolbox
from whitebox import Agent, LoopGuard, Printer, RescueToolCalls, Retry, load_model

QUESTION = "What was the total coffee revenue across all the days in the sales folder?"

if __name__ == "__main__":
    model = Retry(RescueToolCalls(load_model(sys.argv[1] if len(sys.argv) > 1 else None)))
    agent = Agent(model, toolbox, options={"temperature": 0}, hooks=[Printer(), LoopGuard()])
    print(agent.run(QUESTION).answer)
