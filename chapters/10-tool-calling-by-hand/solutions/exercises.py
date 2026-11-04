"""Chapter 10 exercises, solved."""
import json


def request_schema(tool_names):
    return {
        "type": "object",
        "properties": {
            "tool": {"type": "string", "enum": tool_names},
            "arguments": {"type": "object"},
        },
        "required": ["tool", "arguments"],
    }


def read_request(reply):
    request = json.loads(reply)
    return request["tool"], request["arguments"]


def run_tool(tools, name, arguments):
    return str(tools[name](**arguments))


def safe_run_tool(tools, name, arguments):
    if name not in tools:
        return f"Error: there is no tool called {name}"
    try:
        return run_tool(tools, name, arguments)
    except Exception as error:
        return f"Error: {error}"


def round_trip(question, chat, tools):
    messages = [{"role": "user", "content": question}]
    reply = chat(messages)
    name, arguments = read_request(reply)
    result = safe_run_tool(tools, name, arguments)
    messages.append({"role": "assistant", "content": reply})
    messages.append({"role": "user", "content": result})
    return chat(messages)
