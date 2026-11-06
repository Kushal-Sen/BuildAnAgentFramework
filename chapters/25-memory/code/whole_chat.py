"""The finished Memory class on all 36 messages, then a new session for each of the 12 facts."""
import json
from pathlib import Path

from hana import FACTS, OPTIONS, REMEMBER_SYSTEM, SYSTEM, about_hana, chat, recall, right
from whitebox import Agent, Memory, Toolbox, load_model

RUNS = 5
NOTES = Path("whole-chat-notes.json")

model = load_model()
runs = []
for number in range(1, RUNS + 1):
    NOTES.unlink(missing_ok=True)  # Start each run with no notes.
    memory = Memory(NOTES)
    agent = Agent(model, Toolbox([memory.tool()]), system=REMEMBER_SYSTEM, max_steps=4, options=OPTIONS, hooks=[memory])
    for text in chat():
        agent.run(text)
    notes = [note["text"] for note in Memory(NOTES).notes]
    answers = recall(model, memory.system(SYSTEM))
    unwanted = [note for note in notes if not about_hana(note)]
    print(f"run {number}: {len(right(answers)):>2} of {len(FACTS)}, {len(notes)} notes, {len(unwanted)} unwanted", flush=True)
    runs.append({"setup": "Memory", "notes": notes, "answers": answers})
NOTES.unlink(missing_ok=True)
with open("whole-chat.json", "w") as file:
    json.dump(runs, file, indent=1)
