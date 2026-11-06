"""Measure how many tokens the documents are, one file at a time, so nothing gets cut."""
from whitebox import Message, load_documents, load_model

model = load_model()


def tokens(text):
    """Ask for one token of reply, because we only want the count of what went in."""
    return model.chat([Message("user", text)], num_predict=1).tokens_in


empty = tokens("")  # Every request carries a few tokens of wrapping. Take them off.
total, files = 0, 0
for folder in ("handbook", "records"):
    documents = load_documents(f"workspace/{folder}")
    size = sum(tokens(text) - empty for text in documents.values())
    print(f"{folder:<10} {len(documents):>3} files {size:>7,} tokens")
    total += size
    files += len(documents)
print(f"{'together':<10} {files:>3} files {total:>7,} tokens")
