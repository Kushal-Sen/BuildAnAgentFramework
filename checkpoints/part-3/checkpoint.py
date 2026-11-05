"""Part 3 checkpoint. Complete each TODO, then run: python3 -m pytest test_checkpoint.py"""
from pathlib import Path
from typing import Annotated

from whitebox import (
    Agent, Case, Hook, LoopGuard, Model, Retry, Toolbox, contains, finished, load_model, run_eval, tool,
    used_tool,
)

WORKSPACE = Path(__file__).parent / "workspace"


@tool
def list_files(folder: Annotated[str, "Folder path, such as trip"] = ".") -> str:
    """List the files in a folder."""
    return "\n".join(sorted(p.name for p in (WORKSPACE / folder).iterdir()))


@tool
def add_numbers(numbers: Annotated[list[float], "The numbers to add"]) -> float:
    """Add a list of numbers and return the total."""
    return sum(numbers)


# TODO 1: Write find_lines(path, word) as a @tool. It returns the lines of a file in
# WORKSPACE that contain word, ignoring case, joined with newlines. Give it a docstring,
# and describe both parameters with Annotated.


class CountingModel(Model):
    """TODO 2: Wrap another model, and add 1 to self.calls on every chat and every stream.
    Pass everything through to the wrapped model.
    """

    def __init__(self, model):
        self.model = model
        self.calls = 0


class ToolCounter(Hook):
    """TODO 3: Keep a dictionary in self.counts of each tool name and how many times it ran."""

    def __init__(self):
        self.counts = {}


def build_agent(model, counter):
    """TODO 4: Return an Agent with list_files, find_lines and add_numbers. Wrap model in Retry.
    Use the hooks counter and LoopGuard(), and the option temperature 0.7.
    """
    return None


def make_cases():
    """TODO 5: Return two Cases, named "food total" and "hotel total". The food answer is 105,
    and the hotel answer is 180. Each must check the answer, that find_lines was used, and
    that the run finished.
    """
    return []


if __name__ == "__main__":
    model = CountingModel(load_model())
    counter = ToolCounter()
    report = run_eval(build_agent(model, counter), make_cases(), label="trip agent")
    print(report.table())
    print(f"Model calls: {model.calls}. Tool calls: {counter.counts}")
