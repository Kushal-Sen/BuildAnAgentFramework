"""Provided: build the index five times, and check that nothing moves."""
from questions import CODES, DIRECT, REWORDED
from whitebox import Chunk, Index, OllamaEmbedder, load_documents

documents = load_documents("workspace/handbook")
chunks = [Chunk(text, name) for name, text in documents.items()]
questions = [question for question, _ in DIRECT + REWORDED + CODES]


def one_round():
    index = Index(OllamaEmbedder())
    index.add(chunks)
    return [[hit.source for hit in index.search(question, k=3)] for question in questions]


first = one_round()
for number in range(2, 6):
    rankings = one_round()
    same = len([1 for a, b in zip(first, rankings) if a == b])
    print(f"round {number}: {same} of {len(questions)} top 3s match round 1")
