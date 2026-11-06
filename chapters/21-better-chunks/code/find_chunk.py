"""Find the chunk that holds the fact, and see where search ranked it."""
from library import all_documents, build_index, rank_of_text
from whitebox import make_chunks

QUESTION = "How long was the Station card reader down just before Christmas 2025?"
documents = all_documents()

for chunk in make_chunks(documents, 60):
    if "card reader" in chunk.text:
        print(chunk.source)
        print(chunk.text)
        print()
        print("Holds 'Station':", "Station" in chunk.text)

index = build_index(documents, 60)
print("Rank:", rank_of_text(index, QUESTION, "card reader"), "of", len(index.store.rows))
