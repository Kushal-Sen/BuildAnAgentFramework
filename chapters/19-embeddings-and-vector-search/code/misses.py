"""Provided: list where vector search put the right file, for each question it didn't rank first."""
from questions import CODES, DIRECT, REWORDED
from whitebox import Chunk, Index, OllamaEmbedder, load_documents

documents = load_documents("workspace/handbook")
index = Index(OllamaEmbedder())
index.add([Chunk(text, name) for name, text in documents.items()])

for question, right in DIRECT + REWORDED + CODES:
    names = [hit.source for hit in index.search(question, k=len(documents))]
    rank = min(names.index(name) for name in right) + 1
    if rank > 1:
        print(f"rank {rank:2}  {question}")
