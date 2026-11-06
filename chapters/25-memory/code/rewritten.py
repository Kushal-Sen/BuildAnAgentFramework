"""Check each message, and save the model's rewrite of it. Then see what a new session makes of those notes."""
import json

from hana import FACTS, chat, recall, right, with_notes
from whitebox import Message, load_model

RUNS = 5
CHECK = ("Does this one message state a fact about the person writing it? If yes, reply with the fact on one "
         "line starting with '- ', copying names, numbers, dates and times exactly. A question is not a fact. "
         "If no, reply NONE.\n\nMessage: {text}")

if __name__ == "__main__":
    model = load_model()
    runs = []
    for number in range(1, RUNS + 1):
        notes = []
        for text in chat():
            reply = model.chat([Message("user", CHECK.format(text=text))], temperature=0.2).content
            notes += [line[2:].strip() for line in reply.splitlines() if line.startswith("- ")]
        answers = recall(model, with_notes(notes))
        print(f"run {number}: {len(right(answers))} of {len(FACTS)}. Locker: {answers['locker']}", flush=True)
        runs.append({"notes": notes, "answers": answers})
    print("Notes from the last run:", *runs[-1]["notes"], sep="\n  - ")
    with open("rewritten.json", "w") as file:
        json.dump(runs, file, indent=1)
