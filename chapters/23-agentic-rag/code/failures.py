"""Read real runs from the saved agent reports: python3 failures.py hop, none or again. No model is needed."""
import sys

from library import load_runs
from questions import HANDBOOK, RECORDS, says

LABELS = ["agent60", "agent60-again", "agent-hybrid60", "agent-hybrid60-again"]
ROWS = {row[2]: row for row in HANDBOOK + RECORDS}


def name_of(run):
    return ROWS[run["question"]][0]


def passed(run):
    answers = ROWS[run["question"]][3]
    return says(run["answer"], answers) if answers else "don't know" in run["answer"].lower().replace("’", "'")


def show(run, label):
    print(f"{name_of(run)} ({label}), {len(run['searches'])} searches: {run['searches'][0]}")
    print("   ", run["answer"][:270].replace("\n", " "))


runs = [(label, run) for label in LABELS for run in load_runs(f"{label}-runs.json")]

if sys.argv[1] == "hop":  # The questions that need a band, where the answer gave a wrong one.
    for label, run in runs:
        if name_of(run) in ("lead-notice", "shift-lead-pay", "senior-beans") and not passed(run):
            show(run, label)
elif sys.argv[1] == "none":  # Every failure on a question the documents can't answer.
    for label, run in runs:
        if ROWS[run["question"]][1] == "none" and not passed(run):
            show(run, label)
else:  # Every agent60 run that searched more than once.
    for label, run in runs:
        if label in LABELS[:2] and len(run["searches"]) > 1:
            print(f"{name_of(run):<17} {'pass' if passed(run) else 'FAIL'}  {run['searches'][:3]}")
