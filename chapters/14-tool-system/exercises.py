"""Chapter 14 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py

You'll extend the framework in code/whitebox. Don't change anything in that folder.
"""
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


# TODO 1: Write a tool called average, using @tool. It takes one parameter, numbers,
# which is a list of floats with a description. It needs a docstring, and it returns
# the average of the numbers. Replace the line below.
average = None


def signature_line(tool):
    """TODO 2: Return a one-line summary of a tool for a person to read, like this:
    list_files([folder]): List the files in a folder.
    read_file(path): Read a text file.
    Put square brackets around parameters that aren't required. Read tool.parameters.
    """
    return None


def json_type_with_choices(hint):
    """TODO 3: Teach the schema builder about choices. Literal["low", "high"] is a type
    hint that means "one of these strings", and get_origin(hint) is Literal for it.
    For a Literal, return {"type": "string", "enum": [...]}, using get_args(hint).
    For any other hint, return json_type(hint).
    """
    return None


class StrictToolbox(Toolbox):
    """TODO 4: Toolbox.check doesn't look at the types of the arguments. Override check.
    Call super().check first, and return any problem it finds. Then, for each argument,
    look up its JSON type in tool.parameters, and use PYTHON_TYPES and isinstance to test
    the value. If it's wrong, return "Error: <name> must be of type <type>".
    If everything is fine, return None.
    """


class LimitedToolbox(Toolbox):
    """TODO 5: Allow each tool to run only limit times. Add __init__(self, tools=(), limit=2),
    and call super().__init__(tools). Override run to count the calls to each tool name.
    Once a tool goes over the limit, return "Error: <tool> has been used <limit> times already"
    instead of running it. Otherwise, return super().run(call).
    """
