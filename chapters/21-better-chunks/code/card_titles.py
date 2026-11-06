"""The same fact, with and without its title."""
from library import all_documents, build_index, rank_of_text
from whitebox import make_chunks

QUESTION = "How long was the Station card reader down just before Christmas 2025?"
documents = all_documents()

chunks = make_chunks(documents, 60, titles=True)
titled = next(chunk for chunk in chunks if "card reader" in chunk.text)
print(titled.text[:90], "...")
print()

for titles in (False, True):
    index = build_index(documents, 60, titles)
    print(f"titles={titles}: rank {rank_of_text(index, QUESTION, 'card reader')}")

skipped = [chunk for chunk in chunks if chunk.text.startswith("##")]
print(f"{len(skipped)} of {len(chunks)} chunks start with a ## heading, so they get no title")
