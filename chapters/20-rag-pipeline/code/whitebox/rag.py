"""RAG: find the right passages, then answer from them."""
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

import requests

from .agent import Result
from .messages import Message
from .models import ModelError

DEFAULT_EMBEDDER = "nomic-embed-text"


class Embedder:
    """The shape that every embedding model shares."""

    def embed_documents(self, texts):
        raise NotImplementedError

    def embed_query(self, text):
        raise NotImplementedError


class OllamaEmbedder(Embedder):
    """An embedding model served by Ollama."""

    def __init__(self, name=DEFAULT_EMBEDDER, url="http://127.0.0.1:11434", batch=64):
        self.name = name
        self.url = url
        self.batch = batch

    def embed(self, texts):
        """Send texts in batches, because one huge request can fail."""
        vectors = []
        for start in range(0, len(texts), self.batch):
            vectors += self.embed_batch(texts[start:start + self.batch])
        return vectors

    def embed_batch(self, texts):
        body = {"model": self.name, "input": texts}
        try:
            response = requests.post(f"{self.url}/api/embed", json=body, timeout=180)
        except requests.RequestException as error:
            raise ModelError(f"Couldn't reach Ollama: {error}", retryable=True) from error
        if not response.ok:
            raise ModelError(f"Ollama said {response.status_code}: {response.text}", response.status_code >= 500)
        return response.json()["embeddings"]

    def embed_documents(self, texts):
        return self.embed([f"search_document: {text}" for text in texts])

    def embed_query(self, text):
        return self.embed([f"search_query: {text}"])[0]


class FakeEmbedder(Embedder):
    """Counts words into a fixed list of slots. Texts that share words end up close."""

    def __init__(self, size=64):
        self.size = size

    def vector(self, text):
        slots = [0.0] * self.size
        for word in words(text):
            slots[sum(map(ord, word)) % self.size] += 1.0
        return slots

    def embed_documents(self, texts):
        return [self.vector(text) for text in texts]

    def embed_query(self, text):
        return self.vector(text)


def words(text):
    return re.findall(r"[a-z0-9-]+", text.lower())


def cosine(a, b):
    """How closely two vectors point the same way: 1 is identical, 0 is unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    size = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / size if size else 0.0


@dataclass
class Chunk:
    text: str
    source: str


@dataclass
class Hit:
    text: str
    source: str
    score: float


class VectorStore:
    """Keeps every vector in a list, and compares a query with all of them."""

    def __init__(self):
        self.rows = []

    def add(self, chunks, vectors):
        self.rows += [(chunk, vector) for chunk, vector in zip(chunks, vectors)]

    def search(self, vector, k=5):
        hits = [Hit(chunk.text, chunk.source, cosine(vector, row)) for chunk, row in self.rows]
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:k]

    def save(self, path):
        data = [{"text": chunk.text, "source": chunk.source, "vector": vector} for chunk, vector in self.rows]
        Path(path).write_text(json.dumps(data))

    def load(self, path):
        data = json.loads(Path(path).read_text())
        self.rows = [(Chunk(row["text"], row["source"]), row["vector"]) for row in data]


class ChromaStore(VectorStore):
    """The same two methods, backed by the Chroma vector database."""

    def __init__(self, path, name="handbook"):
        import chromadb

        client = chromadb.PersistentClient(path=str(path))
        self.collection = client.get_or_create_collection(name, metadata={"hnsw:space": "cosine"})

    def add(self, chunks, vectors):
        start = self.collection.count()
        self.collection.add(
            ids=[str(start + number) for number in range(len(chunks))],
            embeddings=vectors,
            documents=[chunk.text for chunk in chunks],
            metadatas=[{"source": chunk.source} for chunk in chunks],
        )

    def search(self, vector, k=5):
        found = self.collection.query(query_embeddings=[vector], n_results=k)
        rows = zip(found["documents"][0], found["metadatas"][0], found["distances"][0])
        return [Hit(text, data["source"], 1 - distance) for text, data, distance in rows]


def load_documents(folder):
    """Read every Markdown file in a folder into a dict of name to text."""
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(Path(folder).glob("*.md"))}


def split_text(text, size=120):
    """Split on blank lines, then join paragraphs until a piece reaches about size words."""
    pieces, current = [], []
    for paragraph in re.split(r"\n\s*\n", text.strip()):
        if current and len(" ".join(current).split()) + len(paragraph.split()) > size:
            pieces.append("\n\n".join(current))
            current = []
        current.append(paragraph)
    pieces.append("\n\n".join(current))
    return pieces


def make_chunks(documents, size=120):
    """Split documents into chunks."""
    chunks = []
    for name, text in documents.items():
        for piece in split_text(text, size):
            chunks.append(Chunk(piece, name))
    return chunks


class Index:
    """Embeds chunks into a store, and embeds questions to search it."""

    def __init__(self, embedder, store=None):
        self.embedder = embedder
        self.store = store if store is not None else VectorStore()

    def add(self, chunks):
        self.store.add(chunks, self.embedder.embed_documents([chunk.text for chunk in chunks]))

    def search(self, question, k=5):
        return self.store.search(self.embedder.embed_query(question), k)

RAG_SYSTEM = (
    "Answer the question using only the excerpts below. "
    "After the answer, name the file you used in brackets, such as [uniform.md]. "
    "If the excerpts don't contain the answer, say exactly: I don't know."
)


def excerpts(hits):
    return "\n\n".join(f"[{hit.source}]\n{hit.text}" for hit in hits)


@dataclass
class Rag:
    """The pipeline: search once, put the hits in the prompt, and ask the model."""

    model: object
    index: object
    k: int = 5
    options: dict = field(default_factory=dict)

    def run(self, question):
        hits = self.index.search(question, self.k)
        messages = [
            Message("system", RAG_SYSTEM),
            Message("user", f"Excerpts:\n\n{excerpts(hits)}\n\nQuestion: {question}"),
        ]
        reply = self.model.chat(messages, **self.options)
        return Result(reply.content, messages + [reply], 1)


def hit_rate(index, cases, k=5):
    """The share of cases where every needed file appears in the top k. cases: (question, files)."""
    found = 0
    for question, files in cases:
        sources = {hit.source for hit in index.search(question, k)}
        found += all(name in sources for name in files)
    return found, len(cases)
