"""Worked answers for the chapter 11 exercises."""


def multiply_schema():
    return {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply a list of numbers and return the result.",
            "parameters": {
                "type": "object",
                "properties": {"numbers": {"type": "array", "items": {"type": "number"}}},
                "required": ["numbers"],
            },
        },
    }


def requested_calls(reply):
    return reply.get("tool_calls", [])


def run_tool(call, tools):
    name = call["function"]["name"]
    if name not in tools:
        return f"Error: there is no tool called {name}"
    try:
        return str(tools[name](**call["function"]["arguments"]))
    except Exception as error:
        return f"Error: {error}"


def tool_message(call, result):
    return {"role": "tool", "tool_name": call["function"]["name"], "content": result}


def round_trip(question, chat, tools):
    messages = [{"role": "user", "content": question}]
    reply = chat(messages)
    messages.append(reply)
    calls = requested_calls(reply)
    if not calls:
        return reply["content"]
    for call in calls:
        messages.append(tool_message(call, run_tool(call, tools)))
    return chat(messages)["content"]
