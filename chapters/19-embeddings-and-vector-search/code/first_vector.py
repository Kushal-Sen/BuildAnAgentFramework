"""Turn text into numbers with an embedding model, and look at what comes back."""
from whitebox import OllamaEmbedder

embedder = OllamaEmbedder()
short = embedder.embed_query("footwear")
long = embedder.embed_query("Can I get money back for buying work footwear? " * 20)

print(len(short), len(long))
print([round(number, 3) for number in short[:5]])
