"""Provided helpers for this chapter's scripts, so each script can stay short."""
from whitebox import Index, OllamaEmbedder, load_documents, make_chunks


def all_documents():
    """The handbook and the records, in one dictionary of name to text."""
    return load_documents("workspace/handbook") | load_documents("workspace/records")


def build_index(documents, size):
    """Chunk the documents, embed the chunks, and return the Index."""
    index = Index(OllamaEmbedder())
    index.add(make_chunks(documents, size))
    return index
