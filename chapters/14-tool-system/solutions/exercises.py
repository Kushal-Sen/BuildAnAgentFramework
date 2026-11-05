"""Chapter 14 worked answers."""
from typing import Annotated, Literal, get_args, get_origin

from whitebox import Toolbox, tool
from whitebox.tools import json_type

PYTHON_TYPES = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


@tool
def average(numbers: Annotated[list[float], "The numbers to average"]) -> float:
    """Work out the average of a list of numbers."""
    return sum(numbers) / len(numbers)


def signature_line(tool):
    names = []
    for name in tool.parameters["properties"]:
        names.append(name if name in tool.parameters["required"] else f"[{name}]")
    return f"{tool.name}({', '.join(names)}): {tool.description}"


def json_type_with_choices(hint):
    if get_origin(hint) is Literal:
        return {"type": "string", "enum": list(get_args(hint))}
    return json_type(hint)


class StrictToolbox(Toolbox):
    def check(self, tool, arguments):
        problem = super().check(tool, arguments)
        if problem:
            return problem
        for name, value in arguments.items():
            wanted = tool.parameters["properties"][name]["type"]
            if not isinstance(value, PYTHON_TYPES[wanted]):
                return f"Error: {name} must be of type {wanted}"
        return None


class LimitedToolbox(Toolbox):
    def __init__(self, tools=(), limit=2):
        super().__init__(tools)
        self.limit = limit
        self.counts = {}

    def run(self, call):
        self.counts[call.name] = self.counts.get(call.name, 0) + 1
        if self.counts[call.name] > self.limit:
            return f"Error: {call.name} has been used {self.limit} times already"
        return super().run(call)
