"""Chapter 24 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Trim, newest, total_tokens


def tokens_lost(messages, reply):
    """TODO 1: Return about how many tokens were cut: what we sent, by total_tokens, less what the
    model read, in reply.tokens_in. Never return less than 0, because the estimate is rough.
    """
    return None


def still_has(messages, word):
    """TODO 2: Return True if any message's content has word in it, ignoring case. Use it to see
    whether a fact is still in the chat after a trim.
    """
    return None


def newest_turns(messages, budget):
    """TODO 3: Like newest, but never start on an assistant message, because a reply makes little
    sense without its question. Call newest, then remove messages from the front until the first one
    has role "user". If there isn't one, return an empty list.
    """
    return None


class CountingTrim(Trim):
    """TODO 4: A Trim that adds up how many messages it has removed, in self.removed. Start it at 0.
    Call Trim's own methods with super(), and compare len(messages) before and after.
    """


def missed(agent, history, questions):
    """TODO 5: Ask each question and return the names of the facts the agent got wrong, in order.
    questions holds (name, question, word) tuples, as in staff_chat.py. An answer is right if it has
    word in it, ignoring case. Use agent.run(question, history=history).
    """
    return None
