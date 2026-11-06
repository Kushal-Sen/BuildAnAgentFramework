"""The long test: 120 turns, twelve facts, three runs. Name a setup: window or summarise."""
import json
import sys

from library import OPTIONS
from staff_chat import FACTS, SYSTEM, long_turns, to_messages
from whitebox import Message, Retry, Summarise, load_model, total_tokens

BUDGET = 3000
RUNS = 3
FOR_SUMMARY = {"temperature": 0.2, "num_ctx": 8192}
WINDOW = {**OPTIONS, "num_ctx": 24576}


def play(hook):
    """Play the chat one turn at a time. The hook runs before each reply, as it would inside an Agent."""
    messages, rounds = [Message("system", SYSTEM)], 0
    for question, answer in long_turns():
        messages.append(Message("user", question))
        before = messages[0].content
        hook.before_model(messages)
        rounds += messages[0].content != before
        messages.append(Message("assistant", answer))
    return messages, rounds


def score(model, messages, options):
    """Ask for all twelve facts, and keep each answer so you can read it."""
    rows = []
    for name, _, question, word in FACTS:
        reply = model.chat(messages + [Message("user", question)], **options)
        right = word in reply.content.lower()
        rows.append({"name": name, "right": right, "read": reply.tokens_in, "answer": reply.content})
    return rows


SETUPS = {"window": None, "summarise": Summarise}
label = sys.argv[1]
SETUPS[label]  # A wrong name stops here, before any model call.
model = Retry(load_model())
runs = []
for run in range(1, RUNS + 1):
    if label == "window":
        messages, rounds, options = to_messages(long_turns()), 0, WINDOW
    else:
        messages, rounds = play(SETUPS[label](model, BUDGET, FOR_SUMMARY))
        options = OPTIONS
    rows = score(model, messages, options)
    right = sum(row["right"] for row in rows)
    print(f"{label:<10} run {run}: {right:>2}/12 right  {rounds:>3} summaries  "
          f"sent {total_tokens(messages):>6,}  read {rows[-1]['read']:>6,}", flush=True)
    runs.append({"run": run, "rows": rows, "rounds": rounds, "sent": total_tokens(messages), "system": messages[0].content})
    with open(f"long-{label}.json", "w") as file:
        json.dump(runs, file, indent=1)
print(f"{label:<10} total: {sum(row['right'] for run in runs for row in run['rows'])}/36", flush=True)
