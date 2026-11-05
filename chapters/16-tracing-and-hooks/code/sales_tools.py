"""The sales tools from chapter 12, written with @tool."""
from pathlib import Path
from typing import Annotated

from whitebox import Toolbox, tool

WORKSPACE = Path(__file__).parent / "workspace"


@tool
def list_files(folder: Annotated[str, "Folder path, such as sales"] = ".") -> str:
    """List the files in a folder."""
    return "\n".join(sorted(p.name for p in (WORKSPACE / folder).iterdir()))


@tool
def read_file(path: Annotated[str, "File path, such as sales/monday.txt"]) -> str:
    """Read a text file."""
    return (WORKSPACE / path).read_text()


@tool
def add_numbers(numbers: Annotated[list[float], "The numbers to add"]) -> float:
    """Add a list of numbers and return the total."""
    return sum(numbers)


toolbox = Toolbox([list_files, read_file, add_numbers])
