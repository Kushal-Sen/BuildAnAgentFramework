"""Chapter 22 exercises, with worked answers."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from whitebox import KeywordIndex
from whitebox.rag import words

COMMON = {"what", "is", "for", "the", "a", "an", "how", "do", "does", "i", "my", "to", "of"}


def rarity(total, seen):
    return math.log(1 + (total - seen + 0.5) / (seen + 0.5))


def saturation(found, k1=1.5):
    return found * (k1 + 1) / (found + k1)


class QuestionWords(KeywordIndex):
    def search(self, question, k=5):
        kept = [word for word in words(question) if word not in COMMON]
        return super().search(" ".join(kept), k)


def fuse(rankings, damping=60):
    scores = {}
    for ranking in rankings:
        for rank, name in enumerate(ranking, start=1):
            scores[name] = scores.get(name, 0) + 1 / (damping + rank)
    return sorted(scores, key=lambda name: scores[name], reverse=True)


class Router:
    def __init__(self, vector, keyword):
        self.vector = vector
        self.keyword = keyword

    def add(self, chunks):
        self.vector.add(chunks)
        self.keyword.add(chunks)

    def search(self, question, k=5):
        has_code = any(any(letter.isdigit() for letter in word) for word in words(question))
        return (self.keyword if has_code else self.vector).search(question, k)
