"""Paste the handbook, and ask two questions. Add a number to set num_ctx: python3 paste_try.py 8192"""
import sys

from paste import Paste
from whitebox import Case, contains, load_documents, load_model, run_eval

CASES = [
    Case("shoes", "How much is the shoe allowance?", [contains("40")]),
    Case("e44", "What does E44 mean?", [contains("dose sensor")]),
    Case("names its file", "How much is the shoe allowance?", [contains("[uniform.md]")]),
]

options = {"temperature": 0.7}
if len(sys.argv) > 1:
    options["num_ctx"] = int(sys.argv[1])

paste = Paste(load_model(), load_documents("workspace/handbook"), options)
for case in CASES[:2]:
    result = paste.run(case.question)
    print(f"Q: {case.question}\nA: {result.answer[:160]}")  # Long answers are cut short here.
    print("tokens_in:", result.messages[-1].tokens_in)

print(run_eval(paste, CASES, runs=5, label="five runs each").table())
