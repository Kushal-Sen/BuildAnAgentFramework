"""Chapter 12 exercises, solved."""


def add(a, b):
    return a + b


TOOLS = {"add": add}


def run_tool(call):
    """Provided: run one tool call, as in chapter 11. Errors come back as text."""
    name = call["function"]["name"]
    if name not in TOOLS:
        return f"Error: there is no tool called {name}"
    try:
        return str(TOOLS[name](**call["function"]["arguments"]))
    except Exception as error:
        return f"Error: {error}"


def is_final(reply):
    return not reply.get("tool_calls")


def add_results(messages, calls):
    for call in calls:
        name = call["function"]["name"]
        messages.append({"role": "tool", "tool_name": name, "content": run_tool(call)})


def run_agent(question, chat, max_steps=3):
    messages = [{"role": "user", "content": question}]
    for _ in range(max_steps):
        reply = chat(messages)
        messages.append(reply)
        if is_final(reply):
            return reply["content"]
        add_results(messages, reply["tool_calls"])
    return f"Stopped: no answer after {max_steps} steps."


def tools_used(messages):
    names = []
    for message in messages:
        for call in message.get("tool_calls", []):
            names.append(call["function"]["name"])
    return names
