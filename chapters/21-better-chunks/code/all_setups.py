"""Provided: print every saved report side by side, with no model calls."""
from library import saved
from questions import summary
from whitebox.evals import load_report

ORDER = ["plain60", "plain60-again", "titles60", "titles60-again", "plain120", "titles120", "titles120-again"]

for label in ORDER:
    print(summary(load_report(saved(f"{label}.json"))))
