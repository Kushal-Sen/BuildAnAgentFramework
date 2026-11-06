"""Rank fusion on real questions: why raw scores can't be added, and what can be."""
from library import all_documents, build_hybrid

QUESTIONS = ["How long was the Station card reader down just before Christmas 2025?", "What does E44 mean?"]


def rank(hits, text):
    return next((place for place, hit in enumerate(hits, start=1) if hit.text == text), "-")


index = build_hybrid(all_documents(), 60, titles=True)
vector, keyword = index.indexes

for question in QUESTIONS:
    vector_hits = vector.search(question, index.depth)
    keyword_hits = keyword.search(question, index.depth)
    print(question)
    print(f"  vector scores:  {vector_hits[0].score:.2f} down to {vector_hits[-1].score:.2f}")
    print(f"  keyword scores: {keyword_hits[0].score:.2f} down to {keyword_hits[-1].score:.2f}")
    print(f"  {'Fused':<7} {'Vector':>6} {'Keyword':>7}  File")
    for hit in index.search(question, 4):
        ranks = f"{rank(vector_hits, hit.text):>6} {rank(keyword_hits, hit.text):>7}"
        print(f"  {hit.score:.4f} {ranks}  {hit.source}")
