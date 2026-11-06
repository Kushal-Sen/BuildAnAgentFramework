"""The checks for exercises.py. You don't need to change this file.

They use a fake model, so Ollama doesn't need to be running.
"""
from datetime import date

from exercises import Budgeted, Private, forget, recall_score, unwanted

from whitebox import Agent, FakeModel, Memory, Message, ToolCall, Toolbox


def day(number):
    return lambda: date(2026, 3, number)


def remember():
    return Message("assistant", "", [ToolCall("remember", {"fact": "something"})])


def test_todo_1_unwanted():
    notes = ["My locker is number 212.", "Marek is off with flu.", "I'm allergic to HAZELNUTS.", "ok cool"]
    assert unwanted(notes, ["212", "hazelnut"]) == ["Marek is off with flu.", "ok cool"]
    assert unwanted(notes[:1], ["212"]) == []


def test_todo_2_recall_score():
    model = FakeModel([Message("assistant", "Your locker is 212."), Message("assistant", "I don't know.")])
    questions = [("What's my locker?", "212"), ("What am I allergic to?", "hazelnut")]
    assert recall_score(model, "Be kind.", questions) == 1
    assert [message.role for message in model.seen[0]] == ["system", "user"]
    assert [message.content for message in model.seen[1]] == ["Be kind.", "What am I allergic to?"]
    shouting = FakeModel([Message("assistant", "HAZELNUTS")])
    assert recall_score(shouting, "Be kind.", questions[1:]) == 1


def test_todo_3_forget(tmp_path):
    path = tmp_path / "notes.json"
    memory = Memory(path, day(1))
    memory.add("My locker is number 212.")
    memory.add("I've got a bad knee.")
    memory.add("My KNEE is better now.")
    assert forget(memory, "knee") == 2
    assert [note["text"] for note in memory.notes] == ["My locker is number 212."]
    assert [note["text"] for note in Memory(path).notes] == ["My locker is number 212."]
    assert forget(memory, "lisbon") == 0
    assert [path.name for path in tmp_path.iterdir()] == ["notes.json"]


def test_todo_4_budgeted(tmp_path):
    path = tmp_path / "notes.json"
    memory = Budgeted(path, 30)
    assert memory.system("Be kind.") == "Be kind."
    for letter in "abc":
        memory.add(letter * 40)  # Each note is 14 tokens, so 30 tokens holds two of them.
    text = memory.system("Be kind.")
    assert text.startswith("Be kind.\n\nThings this person told you before, oldest first:\n- ")
    assert "a" * 40 not in text
    assert text.index("b" * 40) < text.index("c" * 40)
    assert len(memory.notes) == 3
    assert len(Memory(path).notes) == 3
    assert Budgeted(path, 1000).system("Be kind.") == Memory(path).system("Be kind.")


def test_todo_5_private(tmp_path):
    memory = Memory(tmp_path / "notes.json")
    replies = [remember(), Message("assistant", "OK.")]
    agent = Agent(FakeModel(list(replies)), Toolbox([memory.tool()]), hooks=[memory, Private(memory, ["password"])])
    result = agent.run("My till PASSWORD is 1234.")
    assert memory.notes == []
    assert [message.content for message in result.messages if message.role == "tool"] == ["Not saved: that looks private."]
    agent = Agent(FakeModel(list(replies)), Toolbox([memory.tool()]), hooks=[memory, Private(memory, ["password"])])
    agent.run("My locker is number 212.")
    assert [note["text"] for note in memory.notes] == ["My locker is number 212."]
