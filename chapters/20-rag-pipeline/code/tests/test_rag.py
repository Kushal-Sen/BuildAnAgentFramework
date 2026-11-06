from whitebox import (
    Chunk, FakeEmbedder, FakeModel, Index, Message, Rag, VectorStore, cosine, hit_rate, split_text,
)

CHUNKS = [
    Chunk("Annual leave is 28 days each year.", "annual-leave.md"),
    Chunk("The grinder code E44 is a dose sensor fault.", "grinder-errors.md"),
    Chunk("Refunds under ten pounds need no approval.", "refunds.md"),
]


def index():
    built = Index(FakeEmbedder())
    built.add(CHUNKS)
    return built


def test_cosine():
    assert cosine([1, 0], [1, 0]) == 1
    assert cosine([1, 0], [0, 1]) == 0
    assert cosine([0, 0], [1, 0]) == 0


def test_search_finds_the_closest():
    assert index().search("annual leave days", 1)[0].source == "annual-leave.md"


def test_search_stops_at_k():
    assert len(index().search("anything", 2)) == 2


def test_store_saves_and_loads(tmp_path):
    store = index().store
    store.save(tmp_path / "store.json")
    loaded = VectorStore()
    loaded.load(tmp_path / "store.json")
    assert loaded.rows == store.rows


def test_split_keeps_small_text_whole():
    assert split_text("one\n\ntwo", size=10) == ["one\n\ntwo"]


def test_split_breaks_at_paragraphs():
    assert split_text("a b c\n\nd e f", size=4) == ["a b c", "d e f"]


def test_rag_puts_hits_in_the_prompt_and_answers():
    model = FakeModel([Message("assistant", "28 days [annual-leave.md]")])
    result = Rag(model, index(), k=1).run("annual leave days")
    assert result.answer.startswith("28")
    assert "Annual leave is 28" in model.seen[0][1].content


def test_hit_rate_needs_every_file():
    cases = [("annual leave", ["annual-leave.md"]), ("annual leave", ["annual-leave.md", "missing.md"])]
    assert hit_rate(index(), cases, k=3) == (1, 2)
