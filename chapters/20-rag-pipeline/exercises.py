"""Chapter 20 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Check

TOKENS_PER_WORD = 1.5  # Provided: about right for these documents, as count_tokens.py measured.


def fits_in_context(documents, num_ctx, room=1000):
    """TODO 1: Return True if every document could be pasted into one prompt. Count the words
    in all the texts, multiply by TOKENS_PER_WORD, and add room for the question and the reply.
    The result must be no more than num_ctx. documents is a dictionary of name to text.
    """
    return None


def fixed_split(text, size):
    """TODO 2: Split text into pieces of exactly size words, ignoring paragraphs. The last piece
    can be shorter. Join each piece's words with one space. Compare it with split_text.
    """
    return None


def chunks_per_file(chunks):
    """TODO 3: Return a dictionary of each source file and how many chunks came from it."""
    return None


def cites(name):
    """TODO 4: Return a Check labeled "cites <name>". It passes when the answer has the file
    name in square brackets, so "cites uniform.md" passes "£40 [uniform.md]".
    """
    return None


def missed(index, cases, k=5):
    """TODO 5: hit_rate counts. This one explains. Return the questions, in order, where at
    least one needed file isn't in the top k. cases is a list of (question, files), as in hit_rate.
    """
    return None
