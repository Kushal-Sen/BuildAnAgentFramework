"""Chapter 22 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from whitebox import KeywordIndex
from whitebox.rag import words

COMMON = {"what", "is", "for", "the", "a", "an", "how", "do", "does", "i", "my", "to", "of"}  # Provided.


def rarity(total, seen):
    """TODO 1: BM25's rarity, by hand. total is how many chunks there are, and seen is how many
    hold the word. Return math.log(1 + (total - seen + 0.5) / (seen + 0.5)).
    """
    return None


def saturation(found, k1=1.5):
    """TODO 2: BM25's saturation for a chunk of average length. Return how much a word that's found
    this many times is worth: found * (k1 + 1) / (found + k1). If found is 0, that gives 0.
    """
    return None


class QuestionWords(KeywordIndex):
    """TODO 3: A KeywordIndex whose search ignores the words in COMMON. Remove them from the
    question with words(question), join what's left with spaces, and call the parent's search.
    """

    def search(self, question, k=5):
        return None


def fuse(rankings, damping=60):
    """TODO 4: Rank fusion by hand. rankings is a list of lists of names, best first. A name
    scores 1 / (damping + rank) in each list it appears in, and rank starts at 1. Return the
    names, highest total first. Names that tie stay in the order they were first seen.
    """
    return None


class Router:
    """TODO 5: Same add and search as an index, and a different inside. add puts the chunks in
    both indexes. search uses keyword if the question holds a word with a digit in it, like E44,
    and vector otherwise. Use words(question), and any(letter.isdigit() for letter in word).
    """

    def __init__(self, vector, keyword):
        self.vector = vector
        self.keyword = keyword

    def add(self, chunks):
        return None

    def search(self, question, k=5):
        return None
