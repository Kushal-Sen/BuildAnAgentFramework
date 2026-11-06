"""Worked answers for chapter 25's exercises."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Hook, Memory, Message, newest


def unwanted(notes, words):
    return [note for note in notes if not any(word in note.lower() for word in words)]


def recall_score(model, system, questions):
    score = 0
    for question, word in questions:
        reply = model.chat([Message("system", system), Message("user", question)])
        score += word in reply.content.lower()
    return score


def forget(memory, word):
    kept = [note for note in memory.notes if word.lower() not in note["text"].lower()]
    removed = len(memory.notes) - len(kept)
    if removed:
        memory.notes = kept
        temporary = memory.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(memory.notes, indent=1))
        os.replace(temporary, memory.path)
    return removed


class Budgeted(Memory):
    def __init__(self, path, budget):
        super().__init__(path)
        self.budget = budget

    def system(self, text):
        kept = newest([Message("user", note["text"]) for note in self.notes], self.budget)
        if not kept:
            return text
        lines = "\n".join(f"- {message.content}" for message in kept)
        return f"{text}\n\nThings this person told you before, oldest first:\n{lines}"


class Private(Hook):
    def __init__(self, memory, words):
        self.memory = memory
        self.words = words

    def before_tool(self, call):
        said = self.memory.latest.lower()
        if call.name == "remember" and any(word in said for word in self.words):
            return "Not saved: that looks private."
        return None
