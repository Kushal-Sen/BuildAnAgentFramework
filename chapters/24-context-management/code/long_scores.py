"""Read the saved long test, fact by fact, or run by run with: python3 long_scores.py sizes. It needs no model."""
import json
import re
import sys

from library import saved
from staff_chat import FACTS

SETUPS = ["window", "summarise"]
MARK = "Earlier in this conversation: "

# What proves the person's own fact is in a note. Plain words won't do: Ravi Nair manages Old Mill, and 06:30 is an opening time.
IN_NOTE = {
    "name": "priya nair", "number": "4471", "day": "college|can't work", "locker": r"\b212\b", "allergy": "cashew",
    "manager": "tomasz", "bus": "07:52", "size": "size 10", "till": "till (three|3)", "sister": "anjali",
    "course": "14 march", "shift": "06:30 tomorrow|tomorrow.{0,30}06:30",
}


def load(label):
    with open(saved(f"long-{label}.json")) as file:
        return json.load(file)


def right(runs, name):
    return sum(row["right"] for run in runs for row in run["rows"] if row["name"] == name)


def noted(runs, name):
    return sum(bool(re.search(IN_NOTE[name], run["system"].partition(MARK)[2].lower())) for run in runs)


def facts(results):
    print("Right answers, and final notes that hold the fact, out of 3 runs")
    print(f"{'Fact':<9} {'Window':>7} {'Summarise':>10} {'In note':>8}")
    window, summarised = results["window"], results["summarise"]
    for name, _, _, _ in FACTS:
        print(f"{name:<9} {right(window, name):>7} {right(summarised, name):>10} {noted(summarised, name):>8}")
    totals = [sum(right(runs, name) for name, _, _, _ in FACTS) for runs in (window, summarised)]
    notes = sum(noted(summarised, name) for name, _, _, _ in FACTS)
    print(f"{'Total':<9} {totals[0]:>7} {totals[1]:>10} {notes:>8}   (of 36)")


def sizes(results):
    print(f"{'Setup':<10} {'Run':>3} {'Right':>6} {'Summaries':>10} {'Sent':>7} {'Read':>7} {'Cheers':>7}")
    for label, runs in results.items():
        for run in runs:
            score = sum(row["right"] for row in run["rows"])
            cheers = sum("cheers" in row["answer"].lower() for row in run["rows"])
            print(f"{label:<10} {run['run']:>3} {score:>6} {run['rounds']:>10} {run['sent']:>7,} "
                  f"{run['rows'][-1]['read']:>7,} {cheers:>4}/12")


if __name__ == "__main__":
    saved_runs = {label: load(label) for label in SETUPS}
    sizes(saved_runs) if sys.argv[1:] == ["sizes"] else facts(saved_runs)
