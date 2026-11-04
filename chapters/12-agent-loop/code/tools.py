"""The tools our agent can use. Each one is an ordinary Python function."""
from pathlib import Path

WORKSPACE = Path(__file__).parent / "workspace"


def list_files(folder: str = ".") -> str:
    """List the files in a folder inside the workspace."""
    return "\n".join(sorted(p.name for p in (WORKSPACE / folder).iterdir()))


def read_file(path: str) -> str:
    """Read a text file inside the workspace."""
    return (WORKSPACE / path).read_text()


def add_numbers(numbers: list) -> float:
    """Add a list of numbers."""
    return sum(float(n) for n in numbers)


TOOLS = {"list_files": list_files, "read_file": read_file, "add_numbers": add_numbers}


def schema(name, description, properties, required):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


SCHEMAS = [
    schema(
        "list_files",
        "List the files in a folder.",
        {"folder": {"type": "string", "description": "Folder path, such as sales"}},
        [],
    ),
    schema(
        "read_file",
        "Read a text file.",
        {"path": {"type": "string", "description": "File path, such as sales/monday.txt"}},
        ["path"],
    ),
    schema(
        "add_numbers",
        "Add a list of numbers and return the total.",
        {"numbers": {"type": "array", "items": {"type": "number"}}},
        ["numbers"],
    ),
]
