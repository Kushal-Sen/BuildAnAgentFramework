"""Provided: chapter 12's loop, given a reply from a provider that isn't Ollama."""
from sales_tools import TOOLS

SYSTEM = "You are a helpful assistant. Use the tools to find facts. Never guess."


def boxy_chat(messages):
    """Boxy is a provider we made up. It has its own way of asking for a tool."""
    return {
        "role": "assistant",
        "content": "",
        "calls": [{"tool": "list_files", "input": {"folder": "sales"}}],
    }


def run_tool(call):
    """Chapter 12's run_tool, unchanged."""
    name = call["function"]["name"]
    if name not in TOOLS:
        return f"Error: there is no tool called {name}"
    try:
        return str(TOOLS[name](**call["function"]["arguments"]))
    except Exception as error:
        return f"Error: {error}"


def run_agent(question, chat, max_steps=8):
    """Chapter 12's run_agent, unchanged."""
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


print("Answer:", repr(run_agent("What's in the sales folder?", boxy_chat)))
