"""Chapter 18 exercises, with worked answers."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Check, tools_used


def numbers_in(text):
    """Provided: return every number in a text. "It cost $1,380.50." gives [1380.5]."""
    return [float(found.replace(",", "")) for found in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]


def equals_number(number):
    return Check(f"equals {number}", lambda result: number in numbers_in(result.answer))


def steps_at_most(limit):
    return Check(f"at most {limit} steps", lambda result: result.steps <= limit)


def tool_count(name, times):
    return Check(f"used {name} {times} times", lambda result: tools_used(result).count(name) == times)


def failed_checks(report):
    counts = {}
    for row in report.rows:
        for failure in row.failures:
            for label in failure["failed"]:
                counts[label] = counts.get(label, 0) + 1
    return counts


def clear_changes(before, after, margin):
    names = []
    for old, new in zip(before.rows, after.rows):
        if abs(new.passed - old.passed) > margin:
            names.append(old.name)
    return names
