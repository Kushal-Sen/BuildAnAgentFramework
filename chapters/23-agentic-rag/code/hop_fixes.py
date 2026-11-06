"""Try one fix on the six hop questions, five runs each: python3 hop_fixes.py check|missing|split"""
import sys

from fixes import CHECK_SYSTEM, AskMissing, Split
from library import OPTIONS, Keep, Remember, all_documents, build_agent, build_index, files_seen
from questions import HANDBOOK, says, strict_pass
from whitebox import load_model

model = load_model()
index = Remember(build_index(all_documents(), 60))

FIXES = {
    "check": lambda: build_agent(model, index, system=CHECK_SYSTEM),
    "missing": lambda: AskMissing(model, index, 3, OPTIONS),
    "split": lambda: Split(model, index, 3, OPTIONS),
}

label = sys.argv[1]
keep = Keep(FIXES[label]())
print(f"{'Question':<18} {'Runs':>4} {'Loose':>6} {'Strict':>7} {'Both files':>11}")
totals = [0, 0, 0, 0]
for name, kind, question, answers, files in [row for row in HANDBOOK if row[1] == "hop"]:
    keep.runs.clear()
    for _ in range(5):
        keep.run(question)
    loose = sum(says(run["answer"], answers) for run in keep.runs)
    strict = sum(strict_pass(run["answer"], name) for run in keep.runs)
    both = sum(set(files) <= set(files_seen(run["seen"])) for run in keep.runs)
    print(f"{name:<18} {5:>4} {loose:>6} {strict:>7} {both:>11}", flush=True)
    totals = [totals[0] + 5, totals[1] + loose, totals[2] + strict, totals[3] + both]
print(f"{'Total':<18} {totals[0]:>4} {totals[1]:>6} {totals[2]:>7} {totals[3]:>11}")
