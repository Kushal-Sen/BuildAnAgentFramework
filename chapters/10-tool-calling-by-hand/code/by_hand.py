"""Tool calling by hand: the model asks for one tool, and our code runs it."""
import json
import sys
from pathlib import Path

import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
WORKSPACE = Path(__file__).parent / "workspace"


def chat(messages, format=None, **options):
    """Send a conversation to the model, and return its reply as text."""
    body = {"model": MODEL, "messages": messages, "stream": False, "options": options}
    if format:
        body["format"] = format
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]["content"]


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

SYSTEM = """You can use one of these tools:
list_files: list the files in a folder. Arguments: {"folder": "sales"}
read_file: read a text file. Arguments: {"path": "sales/monday.txt"}
add_numbers: add a list of numbers. Arguments: {"numbers": [1, 2]}
Reply with the tool to use and its arguments."""

REQUEST = {
    "type": "object",
    "properties": {
        "tool": {"type": "string", "enum": list(TOOLS)},
        "arguments": {"type": "object"},
    },
    "required": ["tool", "arguments"],
}


def dispatch(name, arguments):
    """Run the tool the model asked for. Errors go back to the model as text."""
    if name not in TOOLS:
        return f"Error: there is no tool called {name}"
    try:
        return str(TOOLS[name](**arguments))
    except Exception as error:
        return f"Error: {error}"


def ask(question, chat=chat, **options):
    """One tool request, one result, one final answer."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    reply = chat(messages, format=REQUEST, **options)
    print("Model asked for:", reply)
    request = json.loads(reply)
    result = dispatch(request["tool"], request["arguments"])
    print("Tool returned:", repr(result))
    messages.append({"role": "assistant", "content": reply})
    messages.append({
        "role": "user",
        "content": f"The tool returned:\n{result}\n\nNow answer my question in one sentence.",
    })
    return chat(messages, **options)


if __name__ == "__main__":
    print("Final answer:", ask(" ".join(sys.argv[1:]), temperature=0))
