"""Provided: check that the list store and Chroma agree on every test question."""
from questions import CODES, DIRECT, REWORDED
from whitebox import ChromaStore, Chunk, Index, OllamaEmbedder, VectorStore, load_documents

documents = load_documents("workspace/handbook")
chunks = [Chunk(text, name) for name, text in documents.items()]
embedder = OllamaEmbedder()
vectors = embedder.embed_documents([chunk.text for chunk in chunks])

plain = VectorStore()
plain.add(chunks, vectors)
chroma = ChromaStore("handbook_chroma")
if chroma.collection.count() == 0:
    chroma.add(chunks, vectors)

questions = [question for question, _ in DIRECT + REWORDED + CODES]
same = 0
largest = 0
for question in questions:
    vector = embedder.embed_query(question)
    a = plain.search(vector, k=5)
    b = chroma.search(vector, k=5)
    same += [hit.source for hit in a] == [hit.source for hit in b]
    largest = max([largest] + [abs(x.score - y.score) for x, y in zip(a, b)])
print(f"same top 5, in the same order: {same} of {len(questions)}")
print(f"largest score difference: {largest:.6f}")
