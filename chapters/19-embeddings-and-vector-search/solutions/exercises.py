"""Chapter 19 exercises, with worked answers."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Hit, VectorStore


def unit(vector):
    size = math.sqrt(sum(number * number for number in vector))
    if size == 0:
        return vector
    return [number / size for number in vector]


def above(hits, floor):
    return [hit for hit in hits if hit.score >= floor]


def best_per_source(hits):
    best = {}
    for hit in hits:
        if hit.source not in best or hit.score > best[hit.source].score:
            best[hit.source] = hit
    return sorted(best.values(), key=lambda hit: hit.score, reverse=True)


def rank_of(index, question, source):
    hits = index.search(question, k=len(index.store.rows))
    names = [hit.source for hit in hits]
    if source not in names:
        return None
    return names.index(source) + 1


class UnitStore(VectorStore):
    def add(self, chunks, vectors):
        super().add(chunks, [unit(vector) for vector in vectors])

    def search(self, vector, k=5):
        query = unit(vector)
        hits = []
        for chunk, row in self.rows:
            score = sum(x * y for x, y in zip(query, row))
            hits.append(Hit(chunk.text, chunk.source, score))
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:k]
