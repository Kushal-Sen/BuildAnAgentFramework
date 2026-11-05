"""The checks for exercises.py. You don't need to change this file.

They use fake models and fake failures, so Ollama doesn't need to be running.
"""
from typing import Annotated

import pytest

from exercises import CappedRetry, CountingModel, ToolBudget, rescue_with_words, safe_agent
from whitebox import Agent, FakeModel, Hook, Message, Model, ModelError, ToolCall, Toolbox, tool

ANSWER = Message("assistant", "Done.")


@tool
def ping(text: Annotated[str, "Anything"]) -> str:
    """Say it back."""
    return text


def asks(text):
    return Message("assistant", tool_calls=[ToolCall("ping", {"text": text})])


class AlwaysDown(Model):
    def chat(self, messages, tools=None, **options):
        raise ModelError("Down.", retryable=True)


def test_todo_1_counting_model():
    fake = FakeModel([ANSWER, ANSWER])
    model = CountingModel(fake)
    assert model.chat([Message("user", "Hi")], [ping], temperature=0) == ANSWER
    assert model.calls == 1
    assert fake.seen == [[Message("user", "Hi")]], "pass the messages on to the wrapped model"
    Agent(model).run("Hi")
    assert model.calls == 2, "an Agent can use your wrapper, because it's a Model"


def test_todo_2_capped_retry():
    waits = []
    model = CappedRetry(AlwaysDown(), max_delay=3, attempts=5, sleep=waits.append)
    with pytest.raises(ModelError):
        model.chat([])
    assert waits == [1, 2, 3, 3]


def test_todo_3_rescue_with_words():
    text = 'Sure! {"name": "ping", "arguments": {"text": "hi"}} Hope that helps.'
    reply = rescue_with_words(Message("assistant", text), [ping])
    assert reply.tool_calls == [ToolCall("ping", {"text": "hi"})]
    assert reply.content == ""
    for normal in ["Hello", "Use {curly} braces.", '{"name": "fly"}', "} backwards {"]:
        message = Message("assistant", normal)
        assert rescue_with_words(message, [ping]) == message, "leave normal replies alone"


def test_todo_4_tool_budget():
    budget = ToolBudget(2)
    model = FakeModel([asks("a"), asks("b"), asks("c"), ANSWER, asks("d"), ANSWER])
    agent = Agent(model, Toolbox([ping]), hooks=[budget])
    results = [m.content for m in agent.run("Go").messages if m.role == "tool"]
    assert results[:2] == ["a", "b"]
    assert results[2].startswith("Error: ")
    second = [m.content for m in agent.run("Again").messages if m.role == "tool"]
    assert second == ["d"], "reset the count in on_finish"


def test_todo_5_safe_agent():
    text_call = Message("assistant", '{"name": "ping", "arguments": {"text": "a"}}')
    waits = []
    model = FakeModel([Message("assistant"), text_call, asks("a"), asks("a"), ANSWER])
    agent = safe_agent(model, Toolbox([ping]), sleep=waits.append)
    assert agent is not None, "return an Agent"
    result = agent.run("Go")
    assert waits == [1], "the empty reply should be retried"
    outputs = [m.content for m in result.messages if m.role == "tool"]
    assert outputs[:2] == ["a", "a"], "the text tool call should be rescued"
    assert outputs[2].startswith("Error: you've already"), "the third repeat should be blocked"
    assert result.answer == "Done."
