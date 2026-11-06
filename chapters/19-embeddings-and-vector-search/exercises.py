"""Chapter 19 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Hit, VectorStore


def unit(vector):
    """TODO 1: Return the vector scaled to length 1, by dividing each number by the vector's
    length. The length is the square root of the sum of the squares, as in cosine. A vector
    of all zeros has no direction, so return it unchanged.
    """
    return None


def above(hits, floor):
    """TODO 2: Return only the hits that scored floor or more, in the same order."""
    return None


def best_per_source(hits):
    """TODO 3: Keep only the highest-scoring hit from each source file. Return them sorted
    with the highest score first.
    """
    return None


def rank_of(index, question, source):
    """TODO 4: Search a list-based index for every row, and return where source came: 1 for
    first place, 2 for second, and so on. Return None if source isn't in the index.
    index.store.rows holds every row, so len(index.store.rows) is how many to ask for.
    """
    return None


class UnitStore(VectorStore):
    """TODO 5: A store with the same two methods, and a different inside. add should keep
    each vector as unit(vector), by calling the parent's add. search should score each row
    with a plain dot product against unit(vector), then return the top k hits, best first.
    """

    def add(self, chunks, vectors):
        return None

    def search(self, vector, k=5):
        return None
