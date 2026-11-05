"""Chapter 13 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py

Boxy is the made-up provider from welded.py. This is its format:

    A tool request: {"role": "assistant", "content": "", "calls": [{"tool": "add", "input": {"a": 1}}]}
    A tool result:  {"role": "tool", "tool": "add", "content": "3"}
    Anything else:  {"role": "user", "content": "Hi"}
"""
from whitebox import Message, Model, ToolCall
from whitebox.models import PROVIDERS


def to_boxy(message):
    """TODO 1: Translate one of our Messages into Boxy's format. Always include "role"
    and "content". Add "calls" only if the message has tool calls, and "tool" only if it
    has a tool_name.
    """
    return None


def from_boxy(data):
    """TODO 2: Translate Boxy's reply into a Message with the role "assistant". The
    "calls" key may be missing. Its tools become ToolCalls.
    """
    return None


class BoxyModel(Model):
    """A model served by Boxy. send stands in for the network, as in chapter 05."""

    def __init__(self, name, send=None):
        self.name = name
        self.send = send

    def chat(self, messages, tools=None, **options):
        """TODO 3: Call self.send with {"model": <the name>, "messages": <in Boxy's format>}.
        It returns Boxy's reply. Return that reply as a Message.
        """
        return None


def add_boxy():
    """TODO 4: Add BoxyModel to PROVIDERS, so load_model("boxy/small") can build it."""
    return None


class RuleModel(Model):
    """A model with no AI in it. It adds up any whole numbers in the question."""

    def chat(self, messages, tools=None, **options):
        """TODO 5: Look at the last message.
        If its role is "tool", return an assistant Message: "The total is <its content>."
        If not, split its content into words, keep the words that are all digits, and return
        an assistant Message asking for add_numbers with those numbers as ints. The tool
        takes one argument, called numbers. str.isdigit() tells you if a word is all digits.
        """
        return None
