"""The checks for exercises.py. You don't need to change this file.

They use a fake embedder, so Ollama doesn't need to be running.
"""
from exercises import chunks_with, file_but_no_text, split_at_headings, title_every_chunk, with_overlap

from whitebox import Chunk, FakeEmbedder, Index

CHUNKS = [
    Chunk("Annual leave is 28 days each year.", "annual-leave.md"),
    Chunk("The grinder code E44 is a dose sensor fault.", "grinder-errors.md"),
    Chunk("Refunds under ten pounds need no approval.", "refunds.md"),
]


def test_todo_1_split_at_headings():
    text = "# Title\n\n## One\n\nfirst\n\n## Two\n\nsecond"
    assert split_at_headings(text, 100) == ["# Title\n\n## One\n\nfirst", "## Two\n\nsecond"]
    assert split_at_headings("one two\n\nthree four\n\nfive", 4) == ["one two\n\nthree four", "five"]
    assert split_at_headings("just one", 100) == ["just one"]


def test_todo_2_file_but_no_text():
    index = Index(FakeEmbedder())
    index.add(CHUNKS)
    found = ("leave", "direct", "annual leave", ["28 days"], ["annual-leave.md"])
    no_text = ("wrong", "direct", "annual leave", ["31 days"], ["annual-leave.md"])
    no_file = ("away", "direct", "annual leave", ["28 days"], ["missing.md"])
    assert file_but_no_text(index, [found, no_text, no_file], k=1) == ["wrong"]
    assert file_but_no_text(index, [found], k=1) == []


def test_todo_3_title_every_chunk():
    documents = {"x.md": "# Title\n\n## Monday\n\none two three\n\n## Tuesday\n\nfour five six"}
    chunks = title_every_chunk(documents, size=4)
    assert all(chunk.source == "x.md" for chunk in chunks)
    assert chunks[0].text.startswith("# Title")
    assert not chunks[0].text.startswith("Title\n\n")
    assert any(chunk.text.startswith("Title\n\n## ") for chunk in chunks)
    assert all(chunk.text.startswith(("# Title", "Title\n\n")) for chunk in chunks)


def test_todo_4_chunks_with():
    assert chunks_with(CHUNKS, "e44") == [CHUNKS[1]]
    assert chunks_with(CHUNKS, "LEAVE") == [CHUNKS[0]]
    assert chunks_with(CHUNKS, "missing") == []


def test_todo_5_with_overlap():
    assert with_overlap(["a\n\nb", "c\n\nd", "e"]) == ["a\n\nb", "b\n\nc\n\nd", "d\n\ne"]
    assert with_overlap(["only"]) == ["only"]
    assert with_overlap([]) == []
