"""Worked answers for chapter 26's exercises."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from library import files_seen
from whitebox import Plan, clean


def earned(right, seen, files):
    return right and set(files) <= set(files_seen(seen))


def calls_per_earned(calls, passes):
    if passes == 0:
        return None
    return round(calls / passes, 1)


def drop_label(line):
    label, colon, rest = line.strip().partition(":")
    if colon and label.lower().startswith("step"):
        return clean(rest)
    return clean(line)


class TidyPlan(Plan):
    def make_plan(self, question):
        return [drop_label(step) for step in super().make_plan(question)]


def plans_naming(plans, word):
    return sum(any(word.lower() in step.lower() for step in plan) for plan in plans)
