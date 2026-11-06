"""The same search as search_handbook.py, with Chroma behind the same methods."""
from whitebox import ChromaStore, Chunk, Index, OllamaEmbedder, load_documents

documents = load_documents("workspace/handbook")
chunks = [Chunk(text, name) for name, text in documents.items()]

store = ChromaStore("handbook_chroma")
index = Index(OllamaEmbedder(), store)
if store.collection.count() == 0:
    index.add(chunks)
print(f"{store.collection.count()} rows in Chroma")

for hit in index.search("Can I get money back for buying work footwear?", k=3):
    print(f"  {hit.score:.3f}  {hit.source}")
