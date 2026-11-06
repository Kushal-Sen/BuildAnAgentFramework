"""The checks for exercises.py. You don't need to change this file.

They use a fake embedder, so Ollama doesn't need to be running.
"""
from exercises import QuestionWords, Router, fuse, rarity, saturation

from whitebox import Chunk, FakeEmbedder, Index, KeywordIndex

CHUNKS = [
    Chunk("Annual leave is 28 days each year.", "annual-leave.md"),
    Chunk("The grinder code E44 is a dose sensor fault.", "grinder-errors.md"),
    Chunk("Refunds under ten pounds need no approval.", "refunds.md"),
]


def test_todo_1_rarity():
    assert round(rarity(934, 896), 2) == 0.04
    assert round(rarity(934, 1), 2) == 6.44
    assert rarity(934, 1) > rarity(934, 10) > rarity(934, 500)


def test_todo_2_saturation():
    assert saturation(0) == 0
    assert saturation(1) == 1
    assert round(saturation(2), 2) == 1.43
    assert saturation(1000) < 2.5


def test_todo_3_question_words():
    chunks = [Chunk("what what what is for", "noise.md"), Chunk("FN-6 is the bank form", "forms.md")]
    for _ in range(20):
        chunks.append(Chunk("foggy start and busy morning", "log.md"))
    plain = KeywordIndex()
    plain.add(chunks)
    assert plain.search("What is FN-6 for?", 1)[0].source == "noise.md"
    index = QuestionWords()
    index.add(chunks)
    assert index.search("What is FN-6 for?", 1)[0].source == "forms.md"
    assert index.search("What is for?", 5) == []


def test_todo_4_fuse():
    assert fuse([["a", "b"], ["b", "c"]]) == ["b", "a", "c"]
    assert fuse([["a", "b"], ["b", "a"]]) == ["a", "b"]
    assert fuse([["a", "b", "c"], ["c"]], damping=0) == ["c", "a", "b"]
    assert fuse([]) == []


def test_todo_5_router():
    router = Router(Index(FakeEmbedder()), KeywordIndex())
    router.add(CHUNKS)
    assert len(router.keyword.chunks) == 3
    assert len(router.vector.store.rows) == 3
    assert router.search("What does E44 mean?", 1)[0].source == "grinder-errors.md"
    assert router.search("What does E44 mean?", 1)[0].score != router.vector.search("What does E44 mean?", 1)[0].score
    assert router.search("annual leave days", 1)[0].score == router.vector.search("annual leave days", 1)[0].score
