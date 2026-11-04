"""Chapter 11's round trip, run three times by hand. There's no loop yet."""
from agent import SYSTEM, run_tool, steady_chat

QUESTION = "What was the total coffee revenue across all the days in the sales folder?"

messages = [
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": QUESTION},
]


def one_round():
    """Ask the model once. Run any tools it asks for, and keep everything in messages."""
    reply = steady_chat(messages)
    messages.append(reply)
    calls = reply.get("tool_calls")
    if not calls:
        print("Answer:", reply["content"])
        return
    for call in calls:
        result = run_tool(call)
        print(f"{call['function']['name']}({call['function']['arguments']}) -> {result!r}")
        messages.append(
            {"role": "tool", "tool_name": call["function"]["name"], "content": result}
        )


# Three round trips, one after another.
one_round()
one_round()
one_round()
print(f"The conversation now has {len(messages)} messages.")
