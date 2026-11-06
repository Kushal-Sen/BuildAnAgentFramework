"""The three parts of BM25, with real numbers from the real chunks. No embedding model is used."""
from library import all_documents, build_keyword

index = build_keyword(all_documents(), 60)
print(f"{len(index.chunks)} chunks")

print("\n1. Rarity: a word in fewer chunks is worth more")
for word in ("the", "station", "card", "reader", "fn-6"):
    print(f"  {word:<8} in {index.seen_in[word]:>3} chunks, rarity {index.rarity(word):.2f}")

print("\n2. Saturation: repeats are worth less and less")
for found in (1, 2, 3, 5, 10, 100):
    print(f"  found {found:>3} times: {found * (index.k1 + 1) / (found + index.k1):.2f}")

print("\n3. Length: one match counts for more in a short chunk")
for ratio in (0.5, 1, 2):
    scale = 1 - index.b + index.b * ratio
    print(f"  {ratio:>3}x the average length: {1 * (index.k1 + 1) / (1 + index.k1 * scale):.2f}")
