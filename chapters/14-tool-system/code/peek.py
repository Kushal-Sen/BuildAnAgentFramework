"""Provided: what Python already knows about a function. You don't need to change this file."""
import inspect
import json
from typing import Annotated, get_type_hints

from sales_tools import read_file as built_tool
from whitebox import OllamaModel


def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read a text file."""


def described(path: Annotated[str, "File path, such as sales/monday.txt"]) -> str:
    """Read a text file."""


print("1. The type hints")
print(read_file.__annotations__)

print("2. The docstring")
print(read_file.__doc__)

print("3. The parameters and their defaults")
for name, parameter in inspect.signature(read_file).parameters.items():
    required = parameter.default is inspect.Parameter.empty
    print(name, "required" if required else f"default {parameter.default!r}")

print("4. A type hint that carries a description")
print(get_type_hints(described, include_extras=True)["path"])

print("5. What @tool built")
print(json.dumps(OllamaModel("any").tool_to_ollama(built_tool), indent=1))
