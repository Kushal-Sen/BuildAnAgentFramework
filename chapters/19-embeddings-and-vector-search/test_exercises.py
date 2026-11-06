"""The checks for exercises.py. You don't need to change this file.

They use a fake embedder that counts words, so Ollama doesn't need to be running.
"""
from exercises import UnitStore, above, best_per_source, rank_of, unit
from pytest import approx

from whitebox import Chunk, FakeEmbedder, Hit, Index, VectorStore

CHUNKS = [
    Chunk("Annual leave is 28 days each year.", "annual-leave.md"),
    Chunk("The grinder code E44 is a dose sensor fault.", "grinder-errors.md"),
    Chunk("Refunds under ten pounds need no approval.", "refunds.md"),
]


def index_with(store):
    built = Index(FakeEmbedder(), store)
    built.add(CHUNKS)
    return built


def test_todo_1_unit():
    assert unit([3, 4]) == approx([0.6, 0.8])
    assert unit([0, 2]) == approx([0, 1])
    assert unit([0, 0]) == [0, 0]


def test_todo_2_above():
    hits = [Hit("a", "a.md", 0.9), Hit("b", "b.md", 0.5), Hit("c", "c.md", 0.2)]
    assert above(hits, 0.5) == hits[:2]
    assert above(hits, 0.95) == []


def test_todo_3_best_per_source():
    hits = [Hit("a", "a.md", 0.4), Hit("b", "b.md", 0.6), Hit("a again", "a.md", 0.8), Hit("b", "b.md", 0.6)]
    assert best_per_source(hits) == [Hit("a again", "a.md", 0.8), Hit("b", "b.md", 0.6)]


def test_todo_4_rank_of():
    index = index_with(VectorStore())
    assert rank_of(index, "annual leave days", "annual-leave.md") == 1
    assert rank_of(index, "annual leave days", "grinder-errors.md") in (2, 3)
    assert rank_of(index, "annual leave days", "missing.md") is None


def test_todo_5_unit_store():
    plain = index_with(VectorStore())
    built = index_with(UnitStore())
    question = "the grinder code"
    assert [hit.source for hit in built.search(question, 3)] == [hit.source for hit in plain.search(question, 3)]
    assert len(built.search(question, 2)) == 2
    for mine, theirs in zip(built.search(question, 3), plain.search(question, 3)):
        assert mine.score == approx(theirs.score)
    for _, row in built.store.rows:
        assert sum(number * number for number in row) == approx(1)
