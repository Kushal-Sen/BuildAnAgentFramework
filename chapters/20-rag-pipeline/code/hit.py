"""Measure retrieval alone: does the right file reach the top k? No chat model is used."""
from library import all_documents, build_index
from questions import HANDBOOK, RECORDS, file_cases
from whitebox import Chunk, Index, OllamaEmbedder, hit_rate

cases = file_cases(HANDBOOK + RECORDS)
documents = all_documents()

whole = Index(OllamaEmbedder())
whole.add([Chunk(text, name) for name, text in documents.items()])

print(f"{len(cases)} questions. File hit rate, by k:")
print(f"{'Index':<14} {'k=1':>4} {'k=3':>4} {'k=5':>4}")
indexes = {"whole files": whole, "size 120": build_index(documents, 120), "size 60": build_index(documents, 60)}
for label, index in indexes.items():
    found = [hit_rate(index, cases, k)[0] for k in (1, 3, 5)]
    print(f"{label:<14} {found[0]:>4} {found[1]:>4} {found[2]:>4}")
