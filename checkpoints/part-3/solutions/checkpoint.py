"""Part 3 checkpoint, worked answers. Copy this over ../checkpoint.py to run it."""
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


@tool
def find_lines(
    path: Annotated[str, "File path, such as trip/day1.txt"],
    word: Annotated[str, "The word to look for, such as Hotel"],
) -> str:
    """Find the lines in a text file that contain a word."""
    lines = (WORKSPACE / path).read_text().splitlines()
    return "\n".join(line for line in lines if word.lower() in line.lower())


class CountingModel(Model):
    def __init__(self, model):
        self.model = model
        self.calls = 0

    def chat(self, messages, tools=None, **options):
        self.calls += 1
        return self.model.chat(messages, tools, **options)

    def stream(self, messages, tools=None, **options):
        self.calls += 1
        yield from self.model.stream(messages, tools, **options)


class ToolCounter(Hook):
    def __init__(self):
        self.counts = {}

    def after_tool(self, call, output):
        self.counts[call.name] = self.counts.get(call.name, 0) + 1


def build_agent(model, counter):
    toolbox = Toolbox([list_files, find_lines, add_numbers])
    return Agent(Retry(model), toolbox, hooks=[counter, LoopGuard()], options={"temperature": 0.7})


def make_cases():
    return [
        Case(
            "food total",
            "How much was spent on food across all the days in the trip folder?",
            [contains("105"), used_tool("find_lines"), finished()],
        ),
        Case(
            "hotel total",
            "How much was spent on the hotel across all the days in the trip folder?",
            [contains("180"), used_tool("find_lines"), finished()],
        ),
    ]


if __name__ == "__main__":
    model = CountingModel(load_model())
    counter = ToolCounter()
    report = run_eval(build_agent(model, counter), make_cases(), label="trip agent")
    print(report.table())
    print(f"Model calls: {model.calls}. Tool calls: {counter.counts}")
