"""A complete agent: ask the model, run its tools, repeat until it answers."""
import json
import sys
import urllib.request

from tools import SCHEMAS, TOOLS

URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5:7b"
SYSTEM = "You are a helpful assistant. Use the tools to find facts. Never guess."


def chat(messages):
    """Send the conversation to the model and return its reply."""
    body = {
        "model": MODEL,
        "messages": messages,
        "tools": SCHEMAS,
        "stream": False,
        "options": {"temperature": 0},
    }
    request = urllib.request.Request(
        URL, json.dumps(body).encode(), {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)["message"]


def run_tool(call):
    """Run one tool call. Errors go back to the model so it can recover."""
    name = call["function"]["name"]
    if name not in TOOLS:
        return f"Error: there is no tool called {name}"
    try:
        return str(TOOLS[name](**call["function"]["arguments"]))
    except Exception as error:
        return f"Error: {error}"


def run_agent(question, chat=chat, max_steps=8):
    """Loop until the model answers without asking for a tool."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        reply = chat(messages)
        messages.append(reply)
        calls = reply.get("tool_calls")
        if not calls:
            return reply["content"]
        for call in calls:
            result = run_tool(call)
            print(f"[step {step}] {call['function']['name']}"
                  f"({call['function']['arguments']}) -> {result!r}")
            messages.append(
                {"role": "tool", "tool_name": call["function"]["name"], "content": result}
            )
    return f"Stopped: no answer after {max_steps} steps."


if __name__ == "__main__":
    print(run_agent(" ".join(sys.argv[1:])))
