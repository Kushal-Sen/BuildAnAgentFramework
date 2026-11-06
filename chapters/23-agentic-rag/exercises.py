"""Chapter 22 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Check, Hook


def searched_for(word):
    """TODO 1: Return a Check labeled "searched for <word>". It passes when at least one search
    the agent made has word in its query, ignoring case. Each message in result.messages has
    tool_calls, and each call has arguments, such as {"query": "pay bands"}.
    """
    return None


def found_files(files):
    """TODO 2: Return a Check labeled "found <files>". It passes when every file in the list came
    back from a search. A tool message has role "tool", and each excerpt in its content starts
    with the file name in square brackets, so look for "[uniform.md]".
    """
    return None


def diagnose(result, check, files):
    """TODO 3: Say what happened in one run. Return "right" if check passes. If it fails, return
    "search missed" if a needed file never came back, and "answered badly" if they all did.
    check is a Check, so call check.test(result). You can use found_files.
    """
    return None


def calls_per_question(report):
    """TODO 4: Return the average number of model calls per run in a Report, to one decimal place.
    Each row of report.rows has steps and runs. Use round(number, 1).
    """
    return None


class SearchBudget(Hook):
    """TODO 5: Limit how many searches one run can make. Let the first limit calls through, then
    block each one by returning "Error: no searches left. Answer from what you have." Start
    counting again for the next run. Chapter 17's LoopGuard has the same shape.
    """

    def __init__(self, limit):
        self.limit = limit
