"""Part 2 checkpoint, worked answers."""
from collections import Counter
from pathlib import Path
import sys

import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
SYSTEM = "You are a helpful assistant. Use the tools to find facts. Never guess."
QUESTION = "How much was spent on food across all the days in the trip folder?"
WORKSPACE = Path(__file__).parent.parent / "workspace"


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
    lines = (WORKSPACE / path).read_text().splitlines()
    return "\n".join(line for line in lines if word.lower() in line.lower())


def find_lines_schema():
    return schema(
        "find_lines",
        "Find the lines in a text file that contain a word.",
        {
            "path": {"type": "string", "description": "File path, such as trip/day1.txt"},
            "word": {"type": "string", "description": "The word to look for, such as Hotel"},
        },
        ["path", "word"],
    )


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
    name = call["function"]["name"]
    if name not in TOOLS:
        return f"Error: there is no tool called {name}"
    try:
        return str(TOOLS[name](**call["function"]["arguments"]))
    except Exception as error:
        return f"Error: {error}"


def run_agent(question, chat=chat, max_steps=8):
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    for step in range(max_steps):
        reply = chat(messages)
        messages.append(reply)
        calls = reply.get("tool_calls")
        if not calls:
            return reply["content"], messages
        for call in calls:
            messages.append(
                {"role": "tool", "tool_name": call["function"]["name"], "content": run_tool(call)}
            )
    return f"Stopped: no answer after {max_steps} steps.", messages


def count_tools(messages):
    return dict(Counter(m["tool_name"] for m in messages if m["role"] == "tool"))


if __name__ == "__main__":
    answer, messages = run_agent(" ".join(sys.argv[1:]) or QUESTION)
    print(count_tools(messages))
    print(answer)
