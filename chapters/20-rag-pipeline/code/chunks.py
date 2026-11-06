"""See what make_chunks does to the documents, at different sizes."""
from library import all_documents
from whitebox import make_chunks, split_text

text = "One two three.\n\nFour five six.\n\nSeven eight nine ten eleven."
print(split_text(text, size=5))
print(split_text(text, size=7))
print(split_text(text, size=100))

documents = all_documents()
print(f"\n{len(documents)} files")
for size in (20, 60, 120, 300):
    chunks = make_chunks(documents, size)
    words = sum(len(chunk.text.split()) for chunk in chunks)
    print(f"size {size:>3}: {len(chunks):>4} chunks, {words // len(chunks):>3} words on average")
