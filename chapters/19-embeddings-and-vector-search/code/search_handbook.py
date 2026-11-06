"""Search the handbook by meaning: one vector for each whole file."""
from whitebox import Chunk, Index, OllamaEmbedder, load_documents

documents = load_documents("workspace/handbook")
chunks = [Chunk(text, name) for name, text in documents.items()]

index = Index(OllamaEmbedder())
index.add(chunks)

for question in ["How much is the till float?", "Can I get money back for buying work footwear?"]:
    print(question)
    for hit in index.search(question, k=3):
        print(f"  {hit.score:.3f}  {hit.source}")
