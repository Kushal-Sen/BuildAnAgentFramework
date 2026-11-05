"""Stream the sales agent. usage: python3 demo.py [provider/name]"""
import sys

from sales_tools import toolbox
from whitebox import Agent, load_model

QUESTION = "What was the total coffee revenue across all the days in the sales folder?"

if __name__ == "__main__":
    model = load_model(sys.argv[1] if len(sys.argv) > 1 else None)
    agent = Agent(model, toolbox, options={"temperature": 0})
    for event in agent.stream(QUESTION):
        if event.kind == "text":
            print(event.text, end="", flush=True)
        elif event.kind == "tool_call":
            print(f"[tool] {event.call.name}({event.call.arguments})")
        elif event.kind == "tool_result":
            print(f"    -> {event.text!r}")
    print()
