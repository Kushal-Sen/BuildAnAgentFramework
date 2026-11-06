"""Saying something again, and one place where Memory goes wrong, measured."""
from pathlib import Path

from hana import OPTIONS, REMEMBER_SYSTEM, SYSTEM
from whitebox import Agent, Memory, Message, Toolbox, load_model

RUNS = 5
NOTES = Path("weak-spots-notes.json")
model = load_model()


def fresh():
    NOTES.unlink(missing_ok=True)
    return Memory(NOTES)


# 1. She says something, changes it, then says the first thing again, in the same words.
SAID_AGAIN = [
    (["My locker is number 212.", "My locker is number 87.", "My locker is number 212."], "What's my locker number?"),
    (["Can't do Thursdays.", "Thursdays are fine now.", "Can't do Thursdays."], "Can I work on Thursdays?"),
]
for said, question in SAID_AGAIN:
    memory = fresh()
    for text in said:
        memory.add(text)
    print("Notes kept:", [note["text"] for note in memory.notes])
    system = memory.system(SYSTEM)
    for _ in range(RUNS):
        answer = model.chat([Message("system", system), Message("user", question)], **OPTIONS).content
        print("  ", answer[:100])

# 2. She tells it a fact, and asks to save it in her next message.
for number in range(1, RUNS + 1):
    memory = fresh()
    agent = Agent(model, Toolbox([memory.tool()]), system=REMEMBER_SYSTEM, max_steps=4, options=OPTIONS, hooks=[memory])
    history = agent.run("Can't do Thursdays, I've got a night class in bookkeeping.").messages
    agent.run("Please save that for next time.", history)
    print(f"run {number}:", [note["text"] for note in memory.notes])
NOTES.unlink(missing_ok=True)
