"""Run the sales agent with a trace. usage: python3 demo.py [provider/name]"""
import sys

from sales_tools import toolbox
from whitebox import Agent, Tracer, load_model, show_trace

QUESTION = "What was the total coffee revenue across all the days in the sales folder?"

if __name__ == "__main__":
    model = load_model(sys.argv[1] if len(sys.argv) > 1 else None)
    agent = Agent(model, toolbox, options={"temperature": 0}, hooks=[Tracer("trace.jsonl")])
    agent.run(QUESTION)
    show_trace("trace.jsonl")
