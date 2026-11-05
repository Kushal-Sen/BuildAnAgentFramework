"""Chapter 16 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import json

from whitebox import Hook


class ToolCounter(Hook):
    """TODO 1: Count how many times each tool ran. After a run, self.counts should
    look like {"read_file": 3, "add_numbers": 1}. Use the after_tool moment.
    """

    def __init__(self):
        self.counts = {}


class TokenMeter(Hook):
    """TODO 2: Add up the tokens of every model reply in self.total, counting both
    tokens_in and tokens_out. Use the after_model moment.
    """

    def __init__(self):
        self.total = 0


class Blocklist(Hook):
    """TODO 3: Block every tool named in self.names. Use the before_tool moment, and
    return "Error: <the tool's name> isn't allowed". For other tools, return None.
    """

    def __init__(self, names):
        self.names = names


class ToolLimit(Hook):
    """TODO 4: Allow self.limit tool calls in one run, then block the rest by returning
    "Error: no tool calls left". Start counting again from zero when a run finishes,
    so that one agent can do several runs.
    """

    def __init__(self, limit):
        self.limit = limit
        self.used = 0


def summarize_trace(path):
    """TODO 5: Read a trace file written by Tracer, and return a dictionary like this:
    {"model_calls": 2, "tool_calls": 1, "tokens": 35, "answer": "It's 8."}
    Each line is JSON with a "kind" of "model", "tool" or "finish". For tokens, add up
    tokens_in and tokens_out from the "reply" of each "model" line.
    """
    return None
