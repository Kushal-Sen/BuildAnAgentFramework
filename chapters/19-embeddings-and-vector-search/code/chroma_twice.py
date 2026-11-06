"""What happens if you add the same chunks to Chroma twice."""
import shutil

from whitebox import ChromaStore, Chunk, Index, OllamaEmbedder, load_documents

documents = load_documents("workspace/handbook")
chunks = [Chunk(text, name) for name, text in documents.items()]

shutil.rmtree("chroma_twice", ignore_errors=True)  # Delete the folder, so each run starts empty.
store = ChromaStore("chroma_twice")
index = Index(OllamaEmbedder(), store)
index.add(chunks)
index.add(chunks)

print(f"{store.collection.count()} rows")
for hit in index.search("Can I get money back for buying work footwear?", k=3):
    print(f"  {hit.score:.3f}  {hit.source}")
