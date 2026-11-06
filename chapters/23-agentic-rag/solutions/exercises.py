"""Worked answers for chapter 22's exercises."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Check, Hook


def searched_for(word):
    def test(result):
        queries = [str(call.arguments.get("query", "")) for message in result.messages for call in message.tool_calls]
        return any(word.lower() in query.lower() for query in queries)

    return Check(f"searched for {word}", test)


def found_files(files):
    def test(result):
        seen = "\n".join(message.content for message in result.messages if message.role == "tool")
        return all(f"[{name}]" in seen for name in files)

    return Check(f"found {files}", test)


def diagnose(result, check, files):
    if check.test(result):
        return "right"
    return "answered badly" if found_files(files).test(result) else "search missed"


def calls_per_question(report):
    steps = sum(row.steps for row in report.rows)
    runs = sum(row.runs for row in report.rows)
    return round(steps / runs, 1)


class SearchBudget(Hook):
    def __init__(self, limit):
        self.limit = limit
        self.used = 0

    def before_tool(self, call):
        self.used += 1
        if self.used > self.limit:
            return "Error: no searches left. Answer from what you have."
        return None

    def on_finish(self, result):
        self.used = 0
