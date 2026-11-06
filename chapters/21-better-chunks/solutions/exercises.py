"""Chapter 21 exercises, with worked answers."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))  # Provided: finds code/whitebox.

from library import holds_answer
from whitebox import Chunk, split_text


def split_at_headings(text, size=120):
    pieces, current = [], []
    for paragraph in re.split(r"\n\s*\n", text.strip()):
        too_long = current and len(" ".join(current).split()) + len(paragraph.split()) > size
        has_text = any(not part.startswith("#") for part in current)
        if too_long or (paragraph.startswith("#") and has_text):
            pieces.append("\n\n".join(current))
            current = []
        current.append(paragraph)
    pieces.append("\n\n".join(current))
    return pieces


def file_but_no_text(index, rows, k=5):
    names = []
    for row in rows:
        hits = index.search(row[2], k)
        right_file = any(hit.source in row[4] for hit in hits)
        if right_file and not any(holds_answer(hit, row) for hit in hits):
            names.append(row[0])
    return names


def title_every_chunk(documents, size=120):
    chunks = []
    for name, text in documents.items():
        title = text.splitlines()[0].lstrip("# ")
        for piece in split_text(text, size):
            chunks.append(Chunk(piece if piece.startswith("# ") else f"{title}\n\n{piece}", name))
    return chunks


def chunks_with(chunks, phrase):
    return [chunk for chunk in chunks if phrase.lower() in chunk.text.lower()]


def with_overlap(pieces):
    joined = pieces[:1]
    for before, piece in zip(pieces, pieces[1:]):
        joined.append(before.split("\n\n")[-1] + "\n\n" + piece)
    return joined
