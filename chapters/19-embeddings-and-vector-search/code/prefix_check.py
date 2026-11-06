"""Provided: run every test question with and without nomic-embed-text's task prefixes."""
from questions import CODES, DIRECT, REWORDED
from whitebox import OllamaEmbedder, cosine, load_documents

documents = load_documents("workspace/handbook")
names = list(documents)
embedder = OllamaEmbedder()


def first_place(group, document_vectors, query_prefix):
    wins = 0
    for question, right in group:
        vector = embedder.embed([query_prefix + question])[0]
        scores = [cosine(vector, row) for row in document_vectors]
        wins += names[scores.index(max(scores))] in right
    return wins


with_prefix = embedder.embed_documents(list(documents.values()))
without = embedder.embed(list(documents.values()))
print("Group      With prefixes  Without")
for label, group in [("direct", DIRECT), ("reworded", REWORDED), ("codes", CODES)]:
    print(f"{label:10} {first_place(group, with_prefix, 'search_query: '):7}/{len(group)} "
          f"{first_place(group, without, ''):10}/{len(group)}")
