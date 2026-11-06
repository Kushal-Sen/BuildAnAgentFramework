"""Provided: score every test question against every file, and print the lowest and highest."""
from questions import CODES, DIRECT, REWORDED
from whitebox import Chunk, Index, OllamaEmbedder, load_documents

documents = load_documents("workspace/handbook")
index = Index(OllamaEmbedder())
index.add([Chunk(text, name) for name, text in documents.items()])

scores = []
for question, _ in DIRECT + REWORDED + CODES:
    scores += [hit.score for hit in index.search(question, k=len(documents))]
print(f"{len(scores)} scores, lowest {min(scores):.3f}, highest {max(scores):.3f}")
