"""Chapter 16 exercises, worked answers."""
import json

from whitebox import Hook


class ToolCounter(Hook):
    def __init__(self):
        self.counts = {}

    def after_tool(self, call, output):
        self.counts[call.name] = self.counts.get(call.name, 0) + 1


class TokenMeter(Hook):
    def __init__(self):
        self.total = 0

    def after_model(self, reply):
        self.total += reply.tokens_in + reply.tokens_out


class Blocklist(Hook):
    def __init__(self, names):
        self.names = names

    def before_tool(self, call):
        if call.name in self.names:
            return f"Error: {call.name} isn't allowed"
        return None


class ToolLimit(Hook):
    def __init__(self, limit):
        self.limit = limit
        self.used = 0

    def before_tool(self, call):
        self.used += 1
        if self.used > self.limit:
            return "Error: no tool calls left"
        return None

    def on_finish(self, result):
        self.used = 0


def summarize_trace(path):
    summary = {"model_calls": 0, "tool_calls": 0, "tokens": 0, "answer": ""}
    with open(path) as file:
        for line in file:
            entry = json.loads(line)
            if entry["kind"] == "model":
                summary["model_calls"] += 1
                summary["tokens"] += entry["reply"]["tokens_in"] + entry["reply"]["tokens_out"]
            elif entry["kind"] == "tool":
                summary["tool_calls"] += 1
            else:
                summary["answer"] = entry["answer"]
    return summary
