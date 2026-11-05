"""Provided measuring tool: run one eval several times, and show how far the score moves.

usage: python3 same_agent.py [plain|reliable] [rounds] [provider/name]
"""
import sys

from eval_sales import CASES
from sales_tools import toolbox
from whitebox import Agent, LoopGuard, RescueToolCalls, Retry, load_model, run_eval

if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else "plain"
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    model = load_model(sys.argv[3] if len(sys.argv) > 3 else None)
    options = {"temperature": 0.7}
    if kind == "reliable":
        agent = Agent(Retry(RescueToolCalls(model)), toolbox, options=options, hooks=[LoopGuard()])
    else:
        agent = Agent(model, toolbox, options=options)
    for number in range(1, rounds + 1):
        report = run_eval(agent, CASES, label=kind)
        passed, runs = report.score()
        missed = [f"{row.name} {row.runs - row.passed}" for row in report.rows if row.passed < row.runs]
        print(f"{kind} round {number}: {passed}/{runs}  {', '.join(missed)}", flush=True)
