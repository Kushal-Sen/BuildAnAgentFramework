"""One round trip with native tool calling: the model asks, your code runs it, the model answers."""
import sys

import requests

from tools import SCHEMAS, TOOLS

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
SYSTEM = "You are a helpful assistant. Use the tools to find facts. Never guess."


def chat(messages, **options):
    """Send the conversation and the tools to the model, and return its whole message."""
    body = {"model": MODEL, "messages": messages, "tools": SCHEMAS, "stream": False, "options": options}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]


def run_tool(call):
    """Run one tool call. Errors go back to the model so it can recover."""
    name = call["function"]["name"]
    if name not in TOOLS:
        return f"Error: there is no tool called {name}"
    try:
        return str(TOOLS[name](**call["function"]["arguments"]))
    except Exception as error:
        return f"Error: {error}"


def round_trip(question):
    """Ask once, run the tools the model asks for, then ask once more."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    reply = chat(messages, temperature=0)
    messages.append(reply)
    calls = reply.get("tool_calls")
    if not calls:
        return reply["content"]
    for call in calls:
        result = run_tool(call)
        print(f"[tool] {call['function']['name']}({call['function']['arguments']}) -> {result!r}")
        messages.append(
            {"role": "tool", "tool_name": call["function"]["name"], "content": result}
        )
    reply = chat(messages, temperature=0)
    if reply.get("tool_calls"):
        wanted = reply["tool_calls"][0]["function"]
        return f"Stopped: the model still wants {wanted['name']}({wanted['arguments']})"
    return reply["content"]


if __name__ == "__main__":
    print(round_trip(" ".join(sys.argv[1:])))
