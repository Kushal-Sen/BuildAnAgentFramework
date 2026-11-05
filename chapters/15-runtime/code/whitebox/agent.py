"""The runtime: an Agent you configure once, then run or stream."""
from dataclasses import dataclass, field

from .messages import Message, ToolCall
from .tools import Toolbox

SYSTEM = "You are a helpful assistant. Use the tools to find facts. Never guess."


@dataclass
class Result:
    answer: str
    messages: list[Message]
    steps: int
    stopped: bool = False


@dataclass
class Event:
    """Something that happened during a run. kind is text, tool_call, tool_result or done."""

    kind: str
    text: str = ""
    call: ToolCall | None = None
    result: Result | None = None


@dataclass
class Agent:
    model: object
    toolbox: Toolbox = field(default_factory=Toolbox)
    system: str = SYSTEM
    max_steps: int = 8
    options: dict = field(default_factory=dict)

    def stream(self, question, history=None):
        """Run the loop, yielding an Event for each thing that happens."""
        messages = list(history) if history else [Message("system", self.system)]
        messages.append(Message("user", question))
        for step in range(1, self.max_steps + 1):
            reply = None
            for piece in self.model.stream(messages, self.toolbox.describe(), **self.options):
                if isinstance(piece, Message):
                    reply = piece
                else:
                    yield Event("text", piece)
            messages.append(reply)
            if not reply.tool_calls:
                yield Event("done", result=Result(reply.content, messages, step))
                return
            for call in reply.tool_calls:
                yield Event("tool_call", call=call)
                output = self.toolbox.run(call)
                yield Event("tool_result", output, call=call)
                messages.append(Message("tool", output, tool_name=call.name))
        answer = f"Stopped: no answer after {self.max_steps} steps."
        yield Event("done", result=Result(answer, messages, self.max_steps, stopped=True))

    def run(self, question, history=None):
        """Run the loop to the end and return the Result."""
        for event in self.stream(question, history):
            if event.kind == "done":
                return event.result
