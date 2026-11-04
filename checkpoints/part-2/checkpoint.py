"""Part 2 checkpoint. Complete each TODO, then run: python3 -m pytest test_checkpoint.py"""
from pathlib import Path
import sys

import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
SYSTEM = "You are a helpful assistant. Use the tools to find facts. Never guess."
QUESTION = "How much was spent on food across all the days in the trip folder?"
WORKSPACE = Path(__file__).parent / "workspace"


def list_files(folder: str = ".") -> str:
    """List the files in a folder inside the workspace."""
    return "\n".join(sorted(p.name for p in (WORKSPACE / folder).iterdir()))


def add_numbers(numbers: list) -> float:
    """Add a list of numbers."""
    return sum(float(n) for n in numbers)


def schema(name, description, properties, required):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


def find_lines(path: str, word: str) -> str:
    """TODO 1: Read the file at WORKSPACE / path. Return the lines that contain word,
    ignoring case, joined with newlines.
    """
    return None


def find_lines_schema():
    """TODO 2: Use schema(...) to describe find_lines to the model. Both path and word
    are required strings, and each needs a description.
    """
    return None


TOOLS = {"list_files": list_files, "find_lines": find_lines, "add_numbers": add_numbers}
SCHEMAS = [
    schema(
        "list_files",
        "List the files in a folder.",
        {"folder": {"type": "string", "description": "Folder path, such as trip"}},
        [],
    ),
    schema(
        "add_numbers",
        "Add a list of numbers and return the total.",
        {"numbers": {"type": "array", "items": {"type": "number"}}},
        ["numbers"],
    ),
    find_lines_schema(),
]


def chat(messages, **options):
    """Send the conversation to the model and return its reply."""
    body = {"model": MODEL, "messages": messages, "tools": SCHEMAS, "stream": False, "options": options}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]


def run_tool(call):
    """TODO 3: Run one tool call and return the result as text. Return text starting
    with "Error: " for an unknown tool, or if the tool raises an exception.
    """
    return None


def run_agent(question, chat=chat, max_steps=8):
    """TODO 4: Write the agent loop. Return (answer, messages). If the model is still
    asking for tools after max_steps, return ("Stopped: ...", messages).
    """
    return None, []


def count_tools(messages):
    """TODO 5: Return a dictionary of each tool name and how many times it ran.
    Tool results are the messages with the role "tool".
    """
    return None


if __name__ == "__main__":
    answer, messages = run_agent(" ".join(sys.argv[1:]) or QUESTION)
    print(count_tools(messages))
    print(answer)
