"""Evaluate the sales agent. usage: python3 eval_sales.py [provider/name]"""
import sys

from sales_tools import toolbox
from whitebox import (
    Agent, Case, LoopGuard, RescueToolCalls, Retry, compare, contains, excludes, finished, load_model,
    run_eval, used_no_tools, used_tool,
)

CASES = [
    Case("coffee total", "What was the total coffee revenue across all the days in the sales folder?",
         [contains("380"), used_tool("add_numbers"), finished()]),
    Case("tea total", "What was the total tea revenue across all the days in the sales folder?",
         [contains("245"), finished()]),
    Case("one day", "What was the coffee revenue on Tuesday? The files are in the sales folder.",
         [contains("150"), used_tool("read_file"), finished()]),
    Case("missing day", "What was the coffee revenue on Friday? The files are in the sales folder.",
         [excludes("120"), excludes("150"), excludes("110"), finished()]),
    Case("no tool needed", "Say hello in one short sentence.", [used_no_tools(), finished()]),
]

if __name__ == "__main__":
    plain = load_model(sys.argv[1] if len(sys.argv) > 1 else None)
    options = {"temperature": 0.7}
    before = run_eval(Agent(plain, toolbox, options=options), CASES, label="plain")
    after = run_eval(
        Agent(Retry(RescueToolCalls(plain)), toolbox, options=options, hooks=[LoopGuard()]),
        CASES,
        label="reliable",
    )
    print(before.table())
    print()
    print(after.table())
    print()
    print(compare(before, after))
    before.save("plain.json")
    after.save("reliable.json")
