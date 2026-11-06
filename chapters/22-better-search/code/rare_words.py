"""Why did a question about FN-6 miss? Look at what BM25 thinks is rare in these chunks."""
from library import all_documents, build_keyword

QUESTION = "What is FN-6 used for?"

index = build_keyword(all_documents(), 60)
for word in ("what", "is", "fn-6", "used", "for"):
    print(f"{word:<6} in {index.seen_in[word]:>3} chunks, rarity {index.rarity(word):.2f}")

print(f"\n{QUESTION}")
for hit in index.search(QUESTION, 3):
    print(f"  {hit.score:>5.2f}  {hit.source}")
print("FN-6")
for hit in index.search("FN-6", 3):
    print(f"  {hit.score:>5.2f}  {hit.source}")
