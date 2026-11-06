"""Chapter 20 exercises, with worked answers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from whitebox import Check

TOKENS_PER_WORD = 1.5  # Provided: about right for these documents, as count_tokens.py measured.


def fits_in_context(documents, num_ctx, room=1000):
    words = sum(len(text.split()) for text in documents.values())
    return words * TOKENS_PER_WORD + room <= num_ctx


def fixed_split(text, size):
    words = text.split()
    return [" ".join(words[start:start + size]) for start in range(0, len(words), size)]


def chunks_per_file(chunks):
    counts = {}
    for chunk in chunks:
        counts[chunk.source] = counts.get(chunk.source, 0) + 1
    return counts


def cites(name):
    return Check(f"cites {name}", lambda result: f"[{name}]" in result.answer)


def missed(index, cases, k=5):
    questions = []
    for question, files in cases:
        sources = {hit.source for hit in index.search(question, k)}
        if not all(name in sources for name in files):
            questions.append(question)
    return questions
