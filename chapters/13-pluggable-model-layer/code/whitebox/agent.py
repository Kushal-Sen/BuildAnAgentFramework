"""The agent loop from chapter 12, now talking to any Model."""
from .messages import Message

SYSTEM = "You are a helpful assistant. Use the tools to find facts. Never guess."


def run_tool(call, tools):
    """Run one tool call. Errors go back to the model so it can recover."""
    if call.name not in tools:
        return f"Error: there is no tool called {call.name}"
    try:
        return str(tools[call.name](**call.arguments))
    except Exception as error:
        return f"Error: {error}"


def run_agent(question, model, tools, schemas, max_steps=8, **options):
    """Loop until the model answers without asking for a tool."""
    messages = [Message("system", SYSTEM), Message("user", question)]
    for step in range(1, max_steps + 1):
        reply = model.chat(messages, schemas, **options)
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        for call in reply.tool_calls:
            result = run_tool(call, tools)
            print(f"[step {step}] {call.name}({call.arguments}) -> {result!r}")
            messages.append(Message("tool", result, tool_name=call.name))
    return f"Stopped: no answer after {max_steps} steps."
