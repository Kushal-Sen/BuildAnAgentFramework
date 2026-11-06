"""Chapter 21 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # Provided: finds code/whitebox.

from library import holds_answer
from whitebox import Chunk, split_text


def split_at_headings(text, size=120):
    """TODO 1: Work like split_text, with one more rule, so a heading stays with its text. Before
    adding a paragraph that starts with "#", close the current piece if it holds anything except
    headings. Use re.split(r"\\n\\s*\\n", text.strip()) to get the paragraphs, as split_text does.
    """
    return None


def file_but_no_text(index, rows, k=5):
    """TODO 2: Return the names of the rows where a right file is in the top k, but no hit holds
    the answer. Each row is (name, kind, question, answers, files). holds_answer(hit, row) is
    provided. This is the card reader's kind of failure.
    """
    return None


def title_every_chunk(documents, size=120):
    """TODO 3: Work like make_chunks with titles=True, and also put the title on pieces that start
    with a "##" heading. Only a piece that starts with "# " keeps no extra title, because it
    already has it. Return a list of Chunk. Use split_text(text, size).
    """
    return None


def chunks_with(chunks, phrase):
    """TODO 4: Return the chunks whose text holds phrase, ignoring case. This is what find_chunk.py
    does by hand when you want to see a chunk.
    """
    return None


def with_overlap(pieces):
    """TODO 5: Return the pieces with each one, after the first, starting with the last paragraph
    of the piece before it, then a blank line. So a fact cut off at the end of a piece appears
    in the next one too. Paragraphs are separated by "\\n\\n".
    """
    return None
