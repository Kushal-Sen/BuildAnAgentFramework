"""Run this after TODO 1: the same eval, with chunks cut at headings. Uses your split_at_headings."""
import sys

sys.path.insert(0, "..")  # Finds exercises.py, one folder up.

from exercises import split_at_headings
from library import all_documents, rank_of_text
from questions import HANDBOOK, RECORDS, summary, to_cases
from whitebox import Chunk, Index, OllamaEmbedder, Rag, load_model, run_eval

QUESTION = "How long was the Station card reader down just before Christmas 2025?"


def heading_chunks(documents, titles):
    chunks = []
    for name, text in documents.items():
        title = text.splitlines()[0].lstrip("# ")
        for piece in split_at_headings(text, 60):
            chunks.append(Chunk(f"{title}\n\n{piece}" if titles and not piece.startswith("# ") else piece, name))
    return chunks


documents = all_documents()
cases = to_cases(HANDBOOK + RECORDS)
model = load_model()

for label, titles in (("headings60", False), ("both60", True)):
    index = Index(OllamaEmbedder())
    index.add(heading_chunks(documents, titles))
    report = run_eval(Rag(model, index, 5, {"temperature": 0.7}), cases, runs=3, label=label)
    print(summary(report), flush=True)
    print("  card reader rank:", rank_of_text(index, QUESTION, "card reader"))
    for row in report.rows:
        if row.name in ("records:card-reader", "records:tidewater-fee"):
            print(f"  {row.name}: {row.passed}/{row.runs}", flush=True)
