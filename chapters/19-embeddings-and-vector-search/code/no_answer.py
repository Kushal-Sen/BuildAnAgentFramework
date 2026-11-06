"""Ask questions the handbook can't answer, and compare their scores with real answers."""
from questions import CODES, DIRECT, NOT_IN_HANDBOOK, REWORDED
from whitebox import Chunk, Index, OllamaEmbedder, load_documents

documents = load_documents("workspace/handbook")
index = Index(OllamaEmbedder())
index.add([Chunk(text, name) for name, text in documents.items()])

highest = 0
for question in NOT_IN_HANDBOOK:
    hit = index.search(question, k=1)[0]
    highest = max(highest, hit.score)
    print(f"{hit.score:.3f}  {hit.source:22} {question}")

right = []
for question, files in DIRECT + REWORDED + CODES:
    hit = index.search(question, k=1)[0]
    if hit.source in files:
        right.append(hit.score)
below = len([score for score in right if score < highest])
print(f"{len(right)} right first hits: {below} scored below {highest:.3f}, the highest above")
