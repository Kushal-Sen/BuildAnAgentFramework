"""The same loop as agent.py, with one change: it doesn't keep the conversation."""
from agent import SYSTEM, run_tool, steady_chat

QUESTION = "What was the total coffee revenue across all the days in the sales folder?"


def forgetful_agent(question, chat=steady_chat, max_steps=8):
    for step in range(1, max_steps + 1):
        messages = [  # A fresh conversation on every step.
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ]
        reply = chat(messages)
        calls = reply.get("tool_calls")
        if not calls:
            return reply["content"]
        for call in calls:
            result = run_tool(call)
            print(f"[step {step}] {call['function']['name']}"
                  f"({call['function']['arguments']}) -> {result!r}")
    return f"Stopped: no answer after {max_steps} steps."


if __name__ == "__main__":
    print(forgetful_agent(QUESTION))
