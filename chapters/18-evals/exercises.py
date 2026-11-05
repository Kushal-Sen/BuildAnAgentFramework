"""Chapter 18 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Check, tools_used


def numbers_in(text):
    """Provided: return every number in a text. "It cost $1,380.50." gives [1380.5]."""
    return [float(found.replace(",", "")) for found in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]


def equals_number(number):
    """TODO 1: Return a Check labeled "equals <number>". It passes when number is one of
    the numbers in the answer, so 380 passes "$380.00" but fails "$1,380" and "3800".
    """
    return None


def steps_at_most(limit):
    """TODO 2: Return a Check labeled "at most <limit> steps". It passes when the result
    took no more than limit steps.
    """
    return None


def tool_count(name, times):
    """TODO 3: Return a Check labeled "used <name> <times> times". It passes when the
    model asked for that tool exactly that many times. tools_used(result) lists its calls.
    """
    return None


def failed_checks(report):
    """TODO 4: Return a dictionary of each check's label and how many times it failed.
    Each row in report.rows has failures, and each failure has a "failed" list of labels.
    """
    return None


def clear_changes(before, after, margin):
    """TODO 5: Return the names of the cases whose passed count moved by more than margin,
    in either direction. Both reports list the same cases in the same order.
    """
    return None
