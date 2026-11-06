"""Does the chunk with Tidewater's fee also hold Tidewater's name, at each chunk size?"""
from library import all_documents
from whitebox import make_chunks

documents = all_documents()
for size in (60, 120):
    for chunk in make_chunks(documents, size, titles=True):
        if "£85" in chunk.text and chunk.source == "suppliers.md":
            print(f"size {size}: {len(chunk.text.split())} words, says Tidewater: {'Tidewater' in chunk.text}")
