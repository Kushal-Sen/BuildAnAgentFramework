"""The checks for exercises.py. You don't need to change this file.

They use a fake model, so Ollama doesn't need to be running.
"""
from exercises import CountingTrim, missed, newest_turns, still_has, tokens_lost

from whitebox import Agent, FakeModel, Message, total_tokens


def chat(count):
    messages = [Message("system", "Be kind.")]
    for number in range(count):
        messages += [Message("user", f"Question {number} " + "x" * 40), Message("assistant", f"Answer {number} " + "y" * 40)]
    return messages


def test_todo_1_tokens_lost():
    messages = chat(10)
    sent = total_tokens(messages)
    assert tokens_lost(messages, Message("assistant", "Hi", tokens_in=sent - 50)) == 50
    assert tokens_lost(messages, Message("assistant", "Hi", tokens_in=sent)) == 0
    assert tokens_lost(messages, Message("assistant", "Hi", tokens_in=sent + 9)) == 0


def test_todo_2_still_has():
    messages = [Message("system", "Be kind."), Message("user", "My staff number is 4471, and I'm PRIYA.")]
    assert still_has(messages, "4471") is True
    assert still_has(messages, "priya") is True
    assert still_has(messages, "tomasz") is False
    assert still_has([], "4471") is False


def test_todo_3_newest_turns():
    messages = chat(5)[1:]
    kept = newest_turns(messages, 60)
    assert kept[0].role == "user"
    assert kept[-1].content.startswith("Answer 4")
    assert len(kept) == 2
    assert newest_turns([Message("assistant", "Hello")], 100) == []
    assert newest_turns(messages, 1) == []


def test_todo_4_counting_trim():
    hook = CountingTrim(100)
    assert hook.removed == 0
    short = chat(1)
    hook.before_model(short)
    assert hook.removed == 0
    long = chat(20)
    before = len(long)
    hook.before_model(long)
    assert total_tokens(long) <= 100
    assert hook.removed == before - len(long) > 0
    again = chat(20)
    hook.before_model(again)
    assert hook.removed == 2 * (before - len(long))


def test_todo_5_missed():
    questions = [("name", "My name?", "priya"), ("number", "My number?", "4471"), ("day", "My day?", "tuesday")]
    model = FakeModel([Message("assistant", "You're PRIYA."), Message("assistant", "I'm sorry."), Message("assistant", "Monday.")])
    agent = Agent(model)
    history = chat(1)
    assert missed(agent, history, questions) == ["number", "day"]
    assert len(model.seen[0]) == len(history) + 1
    assert model.seen[0][-1].content == "My name?"
    assert len(model.seen[1]) == len(history) + 1
