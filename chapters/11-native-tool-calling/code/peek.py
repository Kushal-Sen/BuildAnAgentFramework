"""Provided: three looks inside native tool calling. You don't need to change this file."""
import copy
import json

import requests

from native import MODEL, OLLAMA, SYSTEM, chat
from tools import SCHEMAS


def conversation(question):
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]


def first_path(tools):
    """Ask the model to read a file, using these tool definitions, and return the path it chose."""
    question = "Read the Monday sales file."
    body = {"model": MODEL, "messages": conversation(question), "tools": tools, "stream": False}
    reply = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180).json()["message"]
    calls = reply.get("tool_calls")
    return calls[0]["function"]["arguments"].get("path") if calls else None


def without_descriptions():
    """Return a copy of the tool definitions with the parameter descriptions removed."""
    tools = copy.deepcopy(SCHEMAS)
    for tool in tools:
        for parameter in tool["function"]["parameters"]["properties"].values():
            parameter.pop("description", None)
    return tools


def raw_prompt(question):
    """Build the text Ollama gives this model, following the model's own template."""
    tools = "\n".join(json.dumps(tool) for tool in SCHEMAS)
    return f"""<|im_start|>system
{SYSTEM}

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{tools}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{{"name": <function-name>, "arguments": <args-json-object>}}
</tool_call><|im_end|>
<|im_start|>user
{question}<|im_end|>
<|im_start|>assistant
"""


QUESTION = "How much coffee was sold on Monday? The file is sales/monday.txt."

print("1. The whole reply")
print(json.dumps(chat(conversation(QUESTION), temperature=0), indent=1))

print("2. Parameter descriptions")
print("  With:   ", [first_path(SCHEMAS) for _ in range(5)])
print("  Without:", [first_path(without_descriptions()) for _ in range(5)])

print("3. What the model really writes")
body = {"model": MODEL, "prompt": raw_prompt(QUESTION), "raw": True, "stream": False,
        "options": {"temperature": 0, "stop": ["<|im_end|>"]}}
print(requests.post(f"{OLLAMA}/api/generate", json=body, timeout=180).json()["response"])
