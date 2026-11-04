"""Chapter 12 exercises. Fill in the three TODOs, then run: python3 exercises.py

These checks use a scripted fake model, so Ollama doesn't need to be running.
"""


def add(a, b):
    return a + b


def broken():
    raise ValueError("this tool always fails")


TOOLS = {"add": add, "broken": broken}


def run_tool(call):
    name = call["function"]["name"]
    arguments = call["function"]["arguments"]
    # TODO 1: if the tool doesn't exist, return a string starting with "Error:".
    # TODO 2: if the tool raises an exception, return a string starting with "Error:".
    return str(TOOLS[name](**arguments))


def run_agent(question, chat, max_steps=3):
    messages = [{"role": "user", "content": question}]
    while True:  # TODO 3: stop after max_steps and return a string starting with "Stopped:".
        reply = chat(messages)
        messages.append(reply)
        calls = reply.get("tool_calls")
        if not calls:
            return reply["content"]
        for call in calls:
            messages.append({"role": "tool", "content": run_tool(call)})


# ---- Self-check: you don't need to change anything below this line. ----


def tool_call(name, **arguments):
    return {"role": "assistant", "content": "",
            "tool_calls": [{"function": {"name": name, "arguments": arguments}}]}


def scripted(*replies):
    """A fake model that gives each reply in turn."""
    remaining = list(replies)

    def chat(messages):
        scripted.seen = messages
        return remaining.pop(0)

    return chat


def always_calls_add(messages):
    if len(messages) > 50:
        raise RuntimeError("the agent never stopped")
    return tool_call("add", a=1, b=2)


def check_unknown_tool():
    chat = scripted(tool_call("missing"), {"role": "assistant", "content": "done"})
    assert run_agent("hi", chat) == "done"
    assert scripted.seen[2]["content"].startswith("Error:")


def check_tool_exception():
    chat = scripted(tool_call("broken"), {"role": "assistant", "content": "done"})
    assert run_agent("hi", chat) == "done"
    assert scripted.seen[2]["content"].startswith("Error:")


def check_step_limit():
    assert run_agent("hi", always_calls_add, max_steps=3).startswith("Stopped:")


if __name__ == "__main__":
    checks = [("TODO 1: unknown tool", check_unknown_tool),
              ("TODO 2: tool exception", check_tool_exception),
              ("TODO 3: step limit", check_step_limit)]
    passed = 0
    for label, check in checks:
        try:
            check()
            passed += 1
            print(f"PASS  {label}")
        except Exception as error:
            print(f"FAIL  {label}: {type(error).__name__}: {error}")
    print(f"{passed}/{len(checks)} passed")
