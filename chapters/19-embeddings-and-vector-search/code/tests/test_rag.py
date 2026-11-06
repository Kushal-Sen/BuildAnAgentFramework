from whitebox import (
    Chunk, FakeEmbedder, Index, VectorStore, cosine,
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
