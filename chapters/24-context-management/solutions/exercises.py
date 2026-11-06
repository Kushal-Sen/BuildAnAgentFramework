"""Worked answers for chapter 24's exercises."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Trim, newest, total_tokens


def tokens_lost(messages, reply):
    return max(0, total_tokens(messages) - reply.tokens_in)


def still_has(messages, word):
    return any(word.lower() in message.content.lower() for message in messages)


def newest_turns(messages, budget):
    kept = newest(messages, budget)
    while kept and kept[0].role != "user":
        kept.pop(0)
    return kept


class CountingTrim(Trim):
    def __init__(self, budget):
        super().__init__(budget)
        self.removed = 0

    def before_model(self, messages):
        before = len(messages)
        super().before_model(messages)
        self.removed += before - len(messages)


def missed(agent, history, questions):
    wrong = []
    for name, question, word in questions:
        if word.lower() not in agent.run(question, history=history).answer.lower():
            wrong.append(name)
    return wrong
