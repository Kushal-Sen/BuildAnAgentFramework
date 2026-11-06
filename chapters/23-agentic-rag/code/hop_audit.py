"""Read the hop passes: what did the old check accept, and what did the agent actually see?

Name setups to audit those: python3 hop_audit.py split60 split60-again
"""
import sys

from library import files_seen, load_runs
from questions import HANDBOOK, says, strict_pass


def audit(labels):
    runs = [run for label in labels for run in load_runs(f"{label}-runs.json")]
    print(" + ".join(labels))
    print(f"{'Question':<18} {'Runs':>4} {'Loose':>6} {'Strict':>7} {'Both files':>11} {'Searched again':>15}")
    totals = [0, 0, 0, 0]
    for name, kind, question, answers, files in [row for row in HANDBOOK if row[1] == "hop"]:
        mine = [run for run in runs if run["question"] == question]
        loose = sum(says(run["answer"], answers) for run in mine)
        strict = sum(strict_pass(run["answer"], name) for run in mine)
        both = sum(set(files) <= set(files_seen(run["seen"])) for run in mine)
        again = sum(len(run["searches"]) > 1 for run in mine)
        print(f"{name:<18} {len(mine):>4} {loose:>6} {strict:>7} {both:>11} {again:>15}")
        totals = [totals[0] + len(mine), totals[1] + loose, totals[2] + strict, totals[3] + both]
    print(f"{'Total':<18} {totals[0]:>4} {totals[1]:>6} {totals[2]:>7} {totals[3]:>11}\n")


if sys.argv[1:]:
    audit(sys.argv[1:])
else:
    audit(["agent60", "agent60-again"])
    audit(["agent-hybrid60", "agent-hybrid60-again"])
