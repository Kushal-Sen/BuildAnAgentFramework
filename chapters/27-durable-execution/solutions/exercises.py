"""Worked answers for chapter 27's exercises."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Hook, load_messages, once, until_done


def repeats(payments):
    return len(payments) - len(set(payments))


def resume(agent, path, task, again):
    saved = load_messages(path)
    return agent.run(again, saved) if saved else agent.run(task)


def safe_email(send_email, sent):
    return once(send_email, lambda customer, order: (customer, order) in sent)


def still_left(agent, left, ask, history=None, tries=3):
    until_done(agent, left, ask, history, tries)
    return left()


class CallLimit(Hook):
    def __init__(self, name, limit):
        self.name = name
        self.limit = limit
        self.calls = 0

    def before_tool(self, call):
        if call.name != self.name:
            return None
        self.calls += 1
        if self.calls > self.limit:
            return f"Error: too many calls to {self.name}."
        return None

    def on_finish(self, result):
        self.calls = 0
