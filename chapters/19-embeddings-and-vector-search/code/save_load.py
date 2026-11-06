"""Save the store to a file, then load it and search with no document embedding at all."""
from pathlib import Path

from whitebox import Chunk, Index, OllamaEmbedder, VectorStore, load_documents

SAVED = "handbook_vectors.json"
QUESTION = "Can I get money back for buying work footwear?"

documents = load_documents("workspace/handbook")
index = Index(OllamaEmbedder())
index.add([Chunk(text, name) for name, text in documents.items()])
index.store.save(SAVED)
print(f"saved {len(index.store.rows)} rows, {Path(SAVED).stat().st_size:,} bytes")

store = VectorStore()
store.load(SAVED)
reloaded = Index(OllamaEmbedder(), store)
hit = reloaded.search(QUESTION, k=1)[0]
print(f"{hit.score:.3f}  {hit.source}")
