"""Chapter 13 exercises, worked answers."""
from whitebox import Message, Model, ToolCall
from whitebox.models import PROVIDERS


def to_boxy(message):
    data = {"role": message.role, "content": message.content}
    if message.tool_calls:
        data["calls"] = [{"tool": call.name, "input": call.arguments} for call in message.tool_calls]
    if message.tool_name:
        data["tool"] = message.tool_name
    return data


def from_boxy(data):
    calls = [ToolCall(call["tool"], call["input"]) for call in data.get("calls", [])]
    return Message("assistant", data["content"], calls)


class BoxyModel(Model):
    """A model served by Boxy. send stands in for the network, as in chapter 05."""

    def __init__(self, name, send=None):
        self.name = name
        self.send = send

    def chat(self, messages, tools=None, **options):
        body = {"model": self.name, "messages": [to_boxy(message) for message in messages]}
        return from_boxy(self.send(body))


def add_boxy():
    PROVIDERS["boxy"] = BoxyModel


class RuleModel(Model):
    """A model with no AI in it. It adds up any whole numbers in the question."""

    def chat(self, messages, tools=None, **options):
        last = messages[-1]
        if last.role == "tool":
            return Message("assistant", f"The total is {last.content}.")
        numbers = [int(word) for word in last.content.split() if word.isdigit()]
        return Message("assistant", tool_calls=[ToolCall("add_numbers", {"numbers": numbers})])
