"""The same search with the fake embedder. It needs no Ollama, and it knows no meaning."""
from whitebox import Chunk, FakeEmbedder, Index, load_documents

documents = load_documents("workspace/handbook")
index = Index(FakeEmbedder())
index.add([Chunk(text, name) for name, text in documents.items()])

for question in ["How much is the till float?", "Can I get money back for buying work footwear?"]:
    print(question)
    for hit in index.search(question, k=3):
        print(f"  {hit.score:.3f}  {hit.source}")
