"""Provided: chapter 14's run_agent, copied here so you can feel its limits."""
from sales_tools import toolbox
from whitebox import Message, load_model
from whitebox.agent import SYSTEM


def run_agent(question, model, toolbox, max_steps=8, **options):
    """Loop until the model answers without asking for a tool."""
    messages = [Message("system", SYSTEM), Message("user", question)]
    for step in range(1, max_steps + 1):
        reply = model.chat(messages, toolbox.describe(), **options)
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        for call in reply.tool_calls:
            result = toolbox.run(call)
            print(f"[step {step}] {call.name}({call.arguments}) -> {result!r}")
            messages.append(Message("tool", result, tool_name=call.name))
    return f"Stopped: no answer after {max_steps} steps."


if __name__ == "__main__":
    model = load_model()
    print(run_agent("What was the coffee revenue on Monday? The files are in the sales folder.",
                    model, toolbox, temperature=0))
    print(run_agent("And on Tuesday?", model, toolbox, temperature=0))
