"""The checks for exercises.py. You don't need to change this file.

They use a fake model and a fake embedder, so Ollama doesn't need to be running.
"""
from exercises import SearchBudget, calls_per_question, diagnose, found_files, searched_for

from whitebox import Agent, Chunk, FakeEmbedder, FakeModel, Index, Message, Report, Toolbox, ToolCall, contains, search_tool
from whitebox.evals import Row

CHUNKS = [
    Chunk("Shift lead: Band C.", "pay-bands.md"),
    Chunk("Band C staff must give 4 weeks.", "resignation.md"),
]


def index():
    built = Index(FakeEmbedder())
    built.add(CHUNKS)
    return built


def search(query):
    return Message("assistant", "", [ToolCall("search_handbook", {"query": query})])


def run(replies, k=1, hooks=()):
    agent = Agent(FakeModel(replies), Toolbox([search_tool(index(), k)]), hooks=list(hooks))
    return agent.run("How much notice?")


def test_todo_1_searched_for():
    result = run([search("Shift lead BAND"), search("notice"), Message("assistant", "4 weeks")])
    assert searched_for("band").label == "searched for band"
    assert searched_for("band").test(result)
    assert searched_for("NOTICE").test(result)
    assert not searched_for("pension").test(result)


def test_todo_2_found_files():
    both = run([search("anything"), Message("assistant", "4 weeks")], k=2)
    one = run([search("anything"), Message("assistant", "4 weeks")], k=1)
    none = run([Message("assistant", "4 weeks")])
    needed = ["pay-bands.md", "resignation.md"]
    assert found_files(needed).label == f"found {needed}"
    assert found_files(needed).test(both)
    assert not found_files(needed).test(one)
    assert not found_files(needed).test(none)


def test_todo_3_diagnose():
    needed = ["pay-bands.md", "resignation.md"]
    right = contains("4 weeks")
    good = run([search("anything"), Message("assistant", "4 weeks")], k=2)
    bad_answer = run([search("anything"), Message("assistant", "8 weeks")], k=2)
    bad_search = run([search("anything"), Message("assistant", "8 weeks")], k=1)
    assert diagnose(good, right, needed) == "right"
    assert diagnose(bad_answer, right, needed) == "answered badly"
    assert diagnose(bad_search, right, needed) == "search missed"


def test_todo_4_calls_per_question():
    report = Report("agent", [Row("a", runs=3, steps=6), Row("b", runs=3, steps=7)])
    assert calls_per_question(report) == 2.2
    assert calls_per_question(Report("rag", [Row("a", runs=3, steps=3)])) == 1


def test_todo_5_search_budget():
    budget = SearchBudget(1)
    replies = [search("first"), search("second"), Message("assistant", "done")]
    result = run(replies, hooks=[budget])
    outputs = [message.content for message in result.messages if message.role == "tool"]
    assert "[" in outputs[0]
    assert outputs[1] == "Error: no searches left. Answer from what you have."
    again = run([search("third"), Message("assistant", "done")], hooks=[budget])
    assert "[" in [message.content for message in again.messages if message.role == "tool"][0]
