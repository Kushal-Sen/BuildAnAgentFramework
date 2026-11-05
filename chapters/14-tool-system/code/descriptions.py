"""Provided: chapter 11's test, with and without parameter descriptions. You don't need to change this file."""
import copy
from dataclasses import replace

from sales_tools import toolbox
from whitebox import Message, load_model
from whitebox.agent import SYSTEM

model = load_model()


def without_descriptions(tool):
    """Return a copy of a tool with its parameter descriptions removed."""
    parameters = copy.deepcopy(tool.parameters)
    for parameter in parameters["properties"].values():
        parameter.pop("description")
    return replace(tool, parameters=parameters)


def first_path(tools):
    """Ask the model to read a file, and return the path it chose."""
    messages = [Message("system", SYSTEM), Message("user", "Read the Monday sales file.")]
    reply = model.chat(messages, tools)
    return reply.tool_calls[0].arguments.get("path") if reply.tool_calls else None


described = toolbox.describe()
bare = [without_descriptions(tool) for tool in described]
print("With:   ", [first_path(described) for _ in range(5)])
print("Without:", [first_path(bare) for _ in range(5)])
