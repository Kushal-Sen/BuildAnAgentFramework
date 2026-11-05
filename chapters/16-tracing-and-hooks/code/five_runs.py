"""Provided: run both system prompts five times at temperature 0.7, and count what happened."""
from sales_tools import toolbox
from whitebox import Agent, Hook, load_model
from whitebox.agent import SYSTEM

QUESTION = "Which day had the most coffee revenue?"
PROMPTS = {
    "Original prompt": SYSTEM,
    "Better prompt": SYSTEM + " Files are in the sales folder.",
}


class Meter(Hook):
    """Count tokens, tool calls and tool errors for one run."""

    def __init__(self):
        self.tokens = self.tools = self.errors = 0

    def after_model(self, reply):
        self.tokens += reply.tokens_in + reply.tokens_out

    def after_tool(self, call, output):
        self.tools += 1
        self.errors += output.startswith("Error")


model = load_model()
for label, system in PROMPTS.items():
    print(label)
    right = 0
    for run in range(1, 6):
        meter = Meter()
        agent = Agent(model, toolbox, system=system, options={"temperature": 0.7}, hooks=[meter])
        result = agent.run(QUESTION)
        right += "Tuesday" in result.answer
        print(f"  Run {run}: {result.steps} steps, {meter.tools} tool calls, "
              f"{meter.errors} errors, {meter.tokens} tokens")
    print(f"  Named Tuesday: {right}/5")
