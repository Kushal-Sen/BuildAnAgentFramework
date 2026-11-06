"""Score sentences against a question, to see what closeness means for real text."""
from whitebox import OllamaEmbedder, cosine

QUESTION = "Can I get money back for buying work footwear?"
SENTENCES = [
    "After your probation, you can claim a shoe allowance of £40 every 12 months.",
    "Retail beans can be refunded within 30 days if unopened, and with a receipt.",
    "We roast our own beans at the Old Mill roastery every Tuesday and Friday.",
]

embedder = OllamaEmbedder()
question = embedder.embed_query(QUESTION)
vectors = embedder.embed_documents(SENTENCES)
print(QUESTION)
for sentence, vector in zip(SENTENCES, vectors):
    print(f"{cosine(question, vector):.3f}  {sentence}")
