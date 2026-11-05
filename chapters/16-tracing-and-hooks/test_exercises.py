"""The checks for exercises.py. You don't need to change this file.

They use FakeModel, so Ollama doesn't need to be running.
"""
from typing import Annotated

from exercises import Blocklist, TokenMeter, ToolCounter, ToolLimit, summarize_trace
from whitebox import Agent, FakeModel, Message, ToolCall, Toolbox, Tracer, tool


@tool
def double(number: Annotated[int, "The number to double"]) -> int:
    """Double a number."""
    return number * 2


@tool
def shout(text: Annotated[str, "The text to shout"]) -> str:
    """Shout some text."""
    return text.upper()


toolbox = Toolbox([double, shout])
ANSWER = Message("assistant", "It's 8.", tokens_in=20, tokens_out=3)


def asks(name, **arguments):
    return Message("assistant", tool_calls=[ToolCall(name, arguments)], tokens_in=10, tokens_out=2)


def test_todo_1_tool_counter():
    hook = ToolCounter()
    replies = [asks("double", number=1), asks("double", number=2), asks("shout", text="a"), ANSWER]
    Agent(FakeModel(replies), toolbox, hooks=[hook]).run("Go")
    assert hook.counts == {"double": 2, "shout": 1}


def test_todo_2_token_meter():
    hook = TokenMeter()
    Agent(FakeModel([asks("double", number=4), ANSWER]), toolbox, hooks=[hook]).run("Go")
    assert hook.total == 35


def test_todo_3_blocklist():
    hook = Blocklist(["shout"])
    replies = [asks("shout", text="a"), asks("double", number=4), ANSWER]
    messages = Agent(FakeModel(replies), toolbox, hooks=[hook]).run("Go").messages
    results = [message.content for message in messages if message.role == "tool"]
    assert results == ["Error: shout isn't allowed", "8"]


def test_todo_4_tool_limit():
    hook = ToolLimit(1)
    replies = [asks("double", number=1), asks("double", number=2), ANSWER, asks("double", number=3), ANSWER]
    agent = Agent(FakeModel(replies), toolbox, hooks=[hook])
    first = [message.content for message in agent.run("Go").messages if message.role == "tool"]
    second = [message.content for message in agent.run("Again").messages if message.role == "tool"]
    assert first == ["2", "Error: no tool calls left"]
    assert second == ["6"], "start counting again when a run finishes"


def test_todo_5_summarize_trace(tmp_path):
    path = tmp_path / "trace.jsonl"
    Agent(FakeModel([asks("double", number=4), ANSWER]), toolbox, hooks=[Tracer(path)]).run("Go")
    assert summarize_trace(path) == {"model_calls": 2, "tool_calls": 1, "tokens": 35, "answer": "It's 8."}
