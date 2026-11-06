"""Chapter 27 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Hook, load_messages, once, until_done


def repeats(payments):
    """TODO 1: Return how many payments were repeats. payments is a list of order numbers, as Bank.payments
    gives you, so ["A", "B", "A", "A"] holds 2 repeats. This is the count in the crash table.
    """
    return None


def resume(agent, path, task, again):
    """TODO 2: Start or carry on. If path holds a checkpoint, run the agent with again and the saved messages.
    If it doesn't, run it with task. Return the Result. load_messages gives you None when nothing's saved.
    """
    return None


def safe_email(send_email, sent):
    """TODO 3: Return send_email wrapped in once, so nobody gets the same email twice. send_email takes
    customer and order. sent is a list of (customer, order) pairs, and it's the real record here. One
    customer can have two orders, and each of those is a different email.
    """
    return None


def still_left(agent, left, ask, history=None, tries=3):
    """TODO 4: until_done can run out of tries, and it doesn't tell you. Call it with these arguments, then
    return what left() says afterwards, so your code can see what never got done.
    """
    return None


class CallLimit(Hook):
    """TODO 5: Section 4's reply made 77 calls to one tool. Allow the tool called name up to limit times in a
    run, whatever the arguments, and block the rest by returning "Error: too many calls to NAME." from
    before_tool, with the real name in place of NAME. Let every other tool through, by returning None. Start
    counting again in on_finish, so each run gets its own limit.
    """

    def __init__(self, name, limit):
        self.name = name
        self.limit = limit
        self.calls = 0
