"""The checks for exercises.py. You don't need to change this file.

They use a fake model and a fake embedder, so Ollama doesn't need to be running.
"""
from exercises import chunks_per_file, cites, fits_in_context, fixed_split, missed

from whitebox import Chunk, FakeEmbedder, FakeModel, Index, Message, Rag, hit_rate, make_chunks

CHUNKS = [
    Chunk("Annual leave is 28 days each year.", "annual-leave.md"),
    Chunk("The grinder code E44 is a dose sensor fault.", "grinder-errors.md"),
    Chunk("Refunds under ten pounds need no approval.", "refunds.md"),
]


def index():
    built = Index(FakeEmbedder())
    built.add(CHUNKS)
    return built


def test_todo_1_fits_in_context():
    documents = {"a.md": "word " * 2000, "b.md": "word " * 1000}
    assert fits_in_context(documents, 8192)
    assert not fits_in_context(documents, 4096)
    assert fits_in_context(documents, 4500, room=0)
    assert not fits_in_context(documents, 4500, room=1)


def test_todo_2_fixed_split():
    assert fixed_split("one two three four five", 2) == ["one two", "three four", "five"]
    assert fixed_split("one two\n\nthree four", 3) == ["one two three", "four"]
    assert fixed_split("one two", 10) == ["one two"]


def test_todo_3_chunks_per_file():
    documents = {"a.md": "one\n\ntwo\n\nthree", "b.md": "four"}
    assert chunks_per_file(make_chunks(documents, size=1)) == {"a.md": 3, "b.md": 1}
    assert chunks_per_file([]) == {}


def test_todo_4_cites():
    model = FakeModel([Message("assistant", "28 days [annual-leave.md]")])
    result = Rag(model, index(), k=1).run("annual leave days")
    assert cites("annual-leave.md").label == "cites annual-leave.md"
    assert cites("annual-leave.md").test(result)
    assert not cites("refunds.md").test(result)


def test_todo_5_missed():
    found = ("annual leave days", ["annual-leave.md"])
    lost = ("annual leave days", ["annual-leave.md", "missing.md"])
    assert missed(index(), [found, lost], k=3) == ["annual leave days"]
    assert missed(index(), [found], k=3) == []
    cases = [found, lost]
    assert len(missed(index(), cases, k=3)) == len(cases) - hit_rate(index(), cases, k=3)[0]
