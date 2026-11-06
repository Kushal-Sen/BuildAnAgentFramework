"""Rescore every setup with the strict hop check. Reads the saved runs, so no model is needed."""
import sys

from library import load_runs, saved
from questions import HANDBOOK, says, strict_pass
from whitebox import load_report

LABELS = sys.argv[1:] or ["titles60", "titles60-again", "titles120", "hybrid60", "replay", "agent60", "agent60-again",
                          "agent-hybrid60", "agent-hybrid60-again"]
HOPS = {row[2]: row for row in HANDBOOK if row[1] == "hop"}

print(f"{'Setup':<22} {'Old':>7} {'Old hop':>8} {'Strict':>8} {'Strict hop':>11}")
for label in LABELS:
    passed, total = load_report(saved(f"{label}.json")).score()
    hops = [run for run in load_runs(f"{label}-runs.json") if run["question"] in HOPS]
    loose = sum(says(run["answer"], HOPS[run["question"]][3]) for run in hops)
    strict = sum(strict_pass(run["answer"], HOPS[run["question"]][0]) for run in hops)
    print(f"{label:<22} {f'{passed}/{total}':>7} {f'{loose}/18':>8} {f'{passed - loose + strict}/{total}':>8} {f'{strict}/18':>11}")
