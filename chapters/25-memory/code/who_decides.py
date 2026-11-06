"""Three ways to choose what's saved. Each gets the same chat, then a new session asks for the 12 facts."""
import json
import sys
from typing import Annotated

from hana import FACTS, OPTIONS, REMEMBER_SYSTEM, chat, recall, right, with_notes
from rewritten import CHECK
from whitebox import Agent, Message, Toolbox, load_model, tool

RUNS = 5


def code_checks(model):
    """Your code asks about every message, and keeps the user's words when the reply has a fact in it."""
    notes = []
    for text in chat():
        reply = model.chat([Message("user", CHECK.format(text=text))], temperature=0.2).content
        if "- " in reply:
            notes.append(text)
    return notes


def agent_with(model, remember):
    return Agent(model, Toolbox([remember]), system=REMEMBER_SYSTEM, max_steps=4, options=OPTIONS)


def model_words(model):
    """The model calls remember when it wants to, and what it wrote is what's saved."""
    notes = []

    @tool
    def remember(fact: Annotated[str, "The fact to keep, in a short sentence"]) -> str:
        """Save something about the user for future conversations."""
        notes.append(fact)
        return "Saved."

    agent = agent_with(model, remember)
    for text in chat():
        agent.run(text)
    return notes


def user_words(model):
    """The model calls remember when it wants to, and the code saves what the user just said."""
    notes = []
    said = {"latest": ""}

    @tool
    def remember(fact: Annotated[str, "The fact to keep, in a short sentence"]) -> str:
        """Save something about the user for future conversations."""
        if said["latest"] not in notes:
            notes.append(said["latest"])
        return "Saved."

    agent = agent_with(model, remember)
    for text in chat():
        said["latest"] = text
        agent.run(text)
    return notes


SETUPS = {"code checks": code_checks, "model's words": model_words, "user's words": user_words}

if __name__ == "__main__":
    model = load_model()
    runs = []
    for label in sys.argv[1:] or SETUPS:
        for number in range(1, RUNS + 1):
            notes = SETUPS[label](model)
            answers = recall(model, with_notes(notes))
            print(f"{label:<14} run {number}: {len(right(answers)):>2} of {len(FACTS)}, {len(notes)} notes", flush=True)
            runs.append({"setup": label, "notes": notes, "answers": answers})
            with open("who-decides.json", "w") as file:  # Saved after every run, so a stopped job keeps its work.
                json.dump(runs, file, indent=1)
