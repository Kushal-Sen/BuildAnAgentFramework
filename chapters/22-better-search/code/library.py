"""Provided helpers for this chapter's scripts, so each script can stay short."""
from pathlib import Path

from whitebox import HybridIndex, Index, KeywordIndex, OllamaEmbedder, load_documents, make_chunks


def all_documents():
    """The handbook and the records, in one dictionary of name to text."""
    return load_documents("workspace/handbook") | load_documents("workspace/records")


def build_index(documents, size, titles=False):
    """Chunk the documents, embed the chunks, and return the vector Index."""
    index = Index(OllamaEmbedder())
    index.add(make_chunks(documents, size, titles))
    return index


def build_keyword(documents, size, titles=False):
    """The same chunks in a KeywordIndex. No embedding model is used."""
    index = KeywordIndex()
    index.add(make_chunks(documents, size, titles))
    return index


def build_hybrid(documents, size, titles=False):
    """The same chunks in both, joined by a HybridIndex."""
    index = HybridIndex([Index(OllamaEmbedder()), KeywordIndex()])
    index.add(make_chunks(documents, size, titles))
    return index


def holds_answer(hit, row):
    """True if this hit came from a right file, and its text holds one of the row's answers."""
    name, kind, question, answers, files = row
    return hit.source in files and any(answer.lower() in hit.text.lower() for answer in answers)


def text_found(index, rows, k=5):
    """Like hit_rate, but a question only counts if a hit holds the answer text."""
    found = 0
    for row in rows:
        found += any(holds_answer(hit, row) for hit in index.search(row[2], k))
    return found, len(rows)


class Remember:
    """Provided: keeps each question's top 15, so repeat searches don't ask the Reranker again."""

    def __init__(self, index):
        self.index = index
        self.seen = {}

    def search(self, question, k=5):
        if question not in self.seen:
            self.seen[question] = self.index.search(question, 15)
        return self.seen[question][:k]


def rank_of_text(index, question, phrase):
    """Search every chunk, and return where the first chunk holding the phrase came."""
    total = len(index.store.rows) if hasattr(index, "store") else len(index.chunks)
    for rank, hit in enumerate(index.search(question, total), start=1):
        if phrase in hit.text:
            return rank
    return None


def saved(name):
    """Your own results file if you've made one, and otherwise our saved one in results/."""
    return name if Path(name).exists() else f"results/{name}"
