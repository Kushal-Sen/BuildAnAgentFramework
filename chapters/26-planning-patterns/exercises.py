"""Chapter 26 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from library import files_seen
from whitebox import Plan, clean


def earned(right, seen, files):
    """TODO 1: Return True if the answer was right and every name in files is in files_seen(seen).
    right is True or False. seen is the text of the excerpts. files is a list of file names.
    """
    return None


def calls_per_earned(calls, passes):
    """TODO 2: Return the model calls paid for each earned pass, rounded to 1 decimal place, with
    round(number, 1). If there were no earned passes, return None, because nothing was bought.
    """
    return None


def drop_label(line):
    """TODO 3: A model often writes "Step 1: Find the band", and clean leaves the label in. Return the
    line with a leading "Step" label removed, in any case, and cleaned. If the first word isn't
    "step", return clean(line). Use line.partition(":"), which you met in chapter 24.
    """
    return None


class TidyPlan(Plan):
    """TODO 4: A Plan whose steps have no labels. Replace make_plan: call Plan's own with super(), then
    return each step with drop_label applied. run calls make_plan, so you don't need to change run.
    """


def plans_naming(plans, word):
    """TODO 5: plans is a list of plans, and each plan is a list of steps. Return how many plans have
    word in at least one step, ignoring case. Section 8 used this to count plans that name the band.
    """
    return None
