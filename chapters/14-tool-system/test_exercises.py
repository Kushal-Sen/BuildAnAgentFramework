"""The checks for exercises.py. You don't need to change this file.

They use a fake model that gives scripted replies, so Ollama doesn't need to be running.
"""
from typing import Annotated, Literal

from exercises import LimitedToolbox, StrictToolbox, average, json_type_with_choices, signature_line
from whitebox import FakeModel, Message, Tool, ToolCall, run_agent, tool


@tool
def repeat(
    text: Annotated[str, "What to repeat"],
    times: Annotated[int, "How many times"] = 2,
) -> str:
    """Repeat some text."""
    return text * times


def test_todo_1_average():
    assert isinstance(average, Tool), "use @tool"
    assert average([2, 4]) == 3
    numbers = average.parameters["properties"]["numbers"]
    assert numbers["type"] == "array" and numbers["items"] == {"type": "number"}
    assert numbers["description"] and average.description
    assert average.parameters["required"] == ["numbers"]


def test_todo_2_signature_line():
    assert signature_line(repeat) == "repeat(text, [times]): Repeat some text."


def test_todo_3_json_type_with_choices():
    assert json_type_with_choices(Literal["low", "high"]) == {"type": "string", "enum": ["low", "high"]}
    assert json_type_with_choices(int) == {"type": "integer"}
    assert json_type_with_choices(list[str]) == {"type": "array", "items": {"type": "string"}}


def test_todo_4_strict_toolbox():
    toolbox = StrictToolbox([repeat])
    assert toolbox.run(ToolCall("repeat", {"text": "a", "times": 3})) == "aaa"
    assert toolbox.run(ToolCall("repeat", {"text": "a", "times": "3"})) == "Error: times must be of type integer"
    assert toolbox.run(ToolCall("repeat", {})) == "Error: repeat needs text"


def test_todo_5_limited_toolbox():
    asking = Message("assistant", tool_calls=[ToolCall("repeat", {"text": "a"})])
    model = FakeModel([asking, asking, asking, Message("assistant", "Done.")])
    assert run_agent("Go.", model, LimitedToolbox([repeat], limit=2)) == "Done."
    results = [message.content for message in model.seen[-1] if message.role == "tool"]
    assert results == ["aa", "aa", "Error: repeat has been used 2 times already"]
