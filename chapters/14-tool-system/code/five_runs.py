"""Provided: run the sales agent five times and count the right answers. You don't need to change this file."""
import contextlib
import io

from demo import QUESTION
from sales_tools import toolbox
from whitebox import load_model, run_agent

model = load_model()
right = 0
for run in range(1, 6):
    steps = io.StringIO()
    with contextlib.redirect_stdout(steps):
        answer = run_agent(QUESTION, model, toolbox, temperature=0.7)
    right += "380" in answer
    print(f"Run {run}: {steps.getvalue().count('[step')} tool calls. Ends: {answer[-40:]!r}")
print(f"Reached 380: {right}/5")
