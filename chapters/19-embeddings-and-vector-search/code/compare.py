"""Run every test question through word search and vector search, and count the results."""
from questions import CODES, DIRECT, REWORDED
from whitebox import Chunk, Index, OllamaEmbedder, load_documents
from word_search import word_search

documents = load_documents("workspace/handbook")
index = Index(OllamaEmbedder())
index.add([Chunk(text, name) for name, text in documents.items()])


def count(group):
    """Return how often each search put a right file first, and in its top 3."""
    word_first = word_top3 = vector_first = vector_top3 = ties = 0
    for question, right in group:
        by_words = word_search(question, documents)
        names = [name for _, name in by_words]
        by_vectors = [hit.source for hit in index.search(question, k=3)]
        word_first += names[0] in right
        word_top3 += any(name in right for name in names)
        vector_first += by_vectors[0] in right
        vector_top3 += any(name in right for name in by_vectors)
        ties += names[0] in right and by_words[0][0] == by_words[1][0]
    return word_first, word_top3, vector_first, vector_top3, ties


print("Group      Questions  Words 1st  Words top 3  Vectors 1st  Vectors top 3  Tied wins")
for label, group in [("direct", DIRECT), ("reworded", REWORDED), ("codes", CODES)]:
    a, b, c, d, ties = count(group)
    print(f"{label:10} {len(group):9} {a:10} {b:12} {c:12} {d:14} {ties:10}")
