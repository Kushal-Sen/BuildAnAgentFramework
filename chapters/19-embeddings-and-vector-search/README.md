# Chapter 19: Embeddings and vector search

**Time:** about 2 hours. **You'll learn:** how to search by meaning, how far that gets you, and
where it still goes wrong.

## Where we are

In chapter 18, you learned to measure an agent. Part 4 gives the agent something new to work with:
documents it has never seen.

The running example is Quillon Coffee, an invented chain of four coffee shops, with a staff handbook
of 42 short files. A new barista has a question. Somewhere in those files is the answer. Which file?

That sounds like a job for word search. It isn't always, and that's where this chapter starts.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. You'll work in `chapters/19-embeddings-and-vector-search/code`.

This chapter needs a second model. It's small, 274 MB here:

```bash
ollama pull nomic-embed-text
```

Then install this chapter's packages from `code`:

```bash
python3 -m pip install -r requirements.txt
```

Section 10 uses one more package, Chroma, and it has its own install step there. Nothing before that
section needs it.

One file is new in the framework: `whitebox/rag.py`. The handbook is in `workspace/handbook`.
`questions.py`, `misses.py`, `same_five.py`, `prefix_check.py`, `score_range.py` and `same_results.py`
are provided measuring tools. You don't need to change them. The other scripts are explained as you
reach them.

To check the framework itself, run this from `code`:

```bash
python3 -m pytest tests
```

You should see `48 passed`. These tests use a fake embedder, so they don't need Ollama.

## 1. Word search

Here's the obvious way to search. Open [code/word_search.py](code/word_search.py):

```python
def word_search(question, documents, k=3):
    """Score each file by how many of the question's words it holds. Return the top k."""
    wanted = [word for word in words(question) if word not in COMMON]
    scored = []
    for name, text in documents.items():
        found = words(text)
        scored.append((len([word for word in wanted if word in found]), name))
    return sorted(scored, key=lambda pair: pair[0], reverse=True)[:k]
```

- `load_documents` reads every `.md` file in a folder into a dictionary of file name to text.
- `words` lowercases a text, and splits it into a list of words. It uses the `re` module, and you
  don't need to know how.
- `COMMON` is a list of words like "the" and "how", which we skip because they match every file.
- Each file gets a score: how many of the question's other words it holds.
- `sorted` gets two new arguments. `key` is a function that picks what to sort by, here the score,
  the first item in each pair. `reverse=True` puts the highest first. Files that tie stay in their
  old order, so ties go to the file that comes first in the alphabet.

The script asks two questions. The first uses the handbook's own words. The second doesn't.

**Predict:** which files will each one find?

```bash
python3 word_search.py
```

```text
42 files
How much is the till float?
  2  cash-handling.md
  1  closing-checklist.md
  1  opening-checklist.md
Can I get money back for buying work footwear?
  2  expenses.md
  1  cash-handling.md
  1  closing-checklist.md
```

The first is right. The second is wrong, and it doesn't say so. The answer is in `uniform.md`:

```text
After your probation, you can claim a shoe allowance of £40 every 12 months, using form FN-3 with
a receipt.
```

"Footwear" isn't there, and neither is "money". Apart from "can", that sentence shares no word with
the question, so word search has nothing to go on.

You could add "footwear means shoe" to a list. Then "vacation means leave", "quit means resign", and
on and on. People can ask about anything, in any words, so you'd never finish. What we need is a way
to compare *meanings*.

## 2. Text as numbers

An **embedding model** is a different kind of model. It doesn't write a reply. It reads text and
returns a fixed-length list of numbers, called a **vector** or an **embedding**. It was trained so
that texts with similar meanings get similar numbers.

`nomic-embed-text` is the embedding model we'll use. Open [code/first_vector.py](code/first_vector.py):

```python
embedder = OllamaEmbedder()
short = embedder.embed_query("footwear")
long = embedder.embed_query("Can I get money back for buying work footwear? " * 20)

print(len(short), len(long))
print([round(number, 3) for number in short[:5]])
```

`"..." * 20` repeats a string 20 times, so `long` is a much longer text than `short`.

**Predict:** will the longer text give a longer list?

```bash
python3 first_vector.py
```

```text
768 768
[-0.025, 0.086, -0.204, 0.012, -0.008]
```

Both are 768 numbers. One word and a whole paragraph come out the same size, and that's the point:
any two texts can now be compared, number by number.

No single number means anything you could name. Only the whole list does, and only next to another
list from the same model.

## 3. Cosine: how close are two vectors?

Think of a vector as an arrow pointing out from the middle of a graph. `[3, 4]` means 3 across, 4 up.
A 768-number vector is the same idea, with more directions than you can picture. Two arrows that
point the same way mean two similar texts.

**Cosine similarity** measures that. Open [code/whitebox/rag.py](code/whitebox/rag.py):

```python
def cosine(a, b):
    """How closely two vectors point the same way: 1 is identical, 0 is unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    size = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / size if size else 0.0
```

- `dot`, the **dot product**, multiplies the vectors number by number, and adds up the results.
- An arrow's length is the square root of the sum of its squares. `math.sqrt` is Python's square root.
- Dividing by both lengths removes length from the answer, so only direction counts.
- `if size else 0.0` handles a vector of all zeros, which would otherwise divide by zero.

[code/cosine_by_hand.py](code/cosine_by_hand.py) tries it on vectors small enough to check by hand. It
needs no model:

```python
pairs = [
    ([1, 0], [1, 0]),
    ([3, 4], [6, 8]),
    ([1, 0], [1, 1]),
    ([1, 0], [0, 1]),
    ([1, 0], [-1, 0]),
]
for a, b in pairs:
    print(f"{a!s:8} {b!s:8} {cosine(a, b):.3f}")
```

**Predict:** `[6, 8]` is twice as long as `[3, 4]`, in the same direction. What will the score be?
(`:.3f` prints three decimal places.)

```bash
python3 cosine_by_hand.py
```

```text
[1, 0]   [1, 0]   1.000
[3, 4]   [6, 8]   1.000
[1, 0]   [1, 1]   0.707
[1, 0]   [0, 1]   0.000
[1, 0]   [-1, 0]  -1.000
```

Same direction gives 1, whatever the length. At right angles gives 0. Opposite gives -1.

## 4. Real sentences

Now the question from section 1, against three real handbook sentences, with the first cut short.
Open
[code/similar.py](code/similar.py):

```python
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
```

The first sentence shares no useful word with the question. **Predict:** which will score highest?

```bash
python3 similar.py
```

```text
Can I get money back for buying work footwear?
0.691  After your probation, you can claim a shoe allowance of £40 every 12 months.
0.614  Retail beans can be refunded within 30 days if unopened, and with a receipt.
0.476  We roast our own beans at the Old Mill roastery every Tuesday and Friday.
```

The order is right. The shoe allowance came first, and nobody gave the model a list of synonyms.

Look at the numbers, though. The roastery sentence has nothing to do with the question, and it still
scored 0.476. The docstring on `cosine` says 0 is unrelated, which is true of the arithmetic. It isn't
how this model's scores behave. `score_range.py` is a provided script that scores all 22 test
questions you'll meet in section 7 against all 42 files:

```bash
python3 score_range.py
```

```text
924 scores, lowest 0.309, highest 0.829
```

So a score isn't a percentage. Compare scores with each other, for one question. Section 8 comes back
to this.

## 5. The Embedder

`first_vector.py` and `similar.py` used two methods. The framework gives them a shape, the same way
chapter 13 gave every model a shape:

```python
class Embedder:
    """The shape that every embedding model shares."""

    def embed_documents(self, texts):
        raise NotImplementedError

    def embed_query(self, text):
        raise NotImplementedError
```

`OllamaEmbedder` fills that in. Here's the part that does the work:

```python
def embed(self, texts):
    """Send texts in batches, because one huge request can fail."""
    vectors = []
    for start in range(0, len(texts), self.batch):
        vectors += self.embed_batch(texts[start:start + self.batch])
    return vectors

def embed_documents(self, texts):
    return self.embed([f"search_document: {text}" for text in texts])

def embed_query(self, text):
    return self.embed([f"search_query: {text}"])[0]
```

`range(0, len(texts), self.batch)` counts up in steps of 64, so each slice of `texts` is one batch.
`embed_batch` is one `requests.post` to Ollama's `/api/embed`, the same kind of call you made in
chapter 06.

Why two methods? `nomic-embed-text` was trained with those two labels, `search_document:` and
`search_query:`, and its documentation says to use them. A question and the passage that answers it
aren't alike as texts, so the label tells the model which side it's reading.

Did the labels matter here? `prefix_check.py` is a provided script that counts how often the right
file came first, with and without them:

```bash
python3 prefix_check.py
```

```text
Group      With prefixes  Without
direct           8/8          8/8
reworded         4/8          4/8
codes            4/6          5/6
```

16 of 22 against 17 of 22. On this small set, that's no evidence either way, so we follow the model's
documentation and keep them. You'll meet these groups of questions in section 7.

`FakeEmbedder` has the same two methods, and needs no model:

```python
class FakeEmbedder(Embedder):
    """Counts words into a fixed list of slots. Texts that share words end up close."""

    def __init__(self, size=64):
        self.size = size

    def vector(self, text):
        slots = [0.0] * self.size
        for word in words(text):
            slots[sum(map(ord, word)) % self.size] += 1.0
        return slots
```

`ord` turns a letter into its number, `map` applies it to each letter, and `sum` adds them up. `%` is
the remainder from chapter 01, which keeps that total inside the 64 slots. So each word always lands
in the same slot, and texts sharing words get similar vectors. Nothing here knows what a word means.

That's enough for the tests. They check that the plumbing works, without Ollama. It's the fake model
from chapter 13 again.

## 6. A store and an index

Now you need somewhere to keep the vectors. Two small dataclasses come first. A `Chunk` is a piece of
text and the file it came from. A `Hit` is a search result, which is a chunk with a score:

```python
@dataclass
class Chunk:
    text: str
    source: str


@dataclass
class Hit:
    text: str
    source: str
    score: float
```

In this chapter, each chunk is one whole handbook file.

A **vector store** keeps vectors, and finds the ones closest to a query. This one is a plain list:

```python
class VectorStore:
    """Keeps every vector in a list, and compares a query with all of them."""

    def __init__(self):
        self.rows = []

    def add(self, chunks, vectors):
        self.rows += [(chunk, vector) for chunk, vector in zip(chunks, vectors)]

    def search(self, vector, k=5):
        hits = [Hit(chunk.text, chunk.source, cosine(vector, row)) for chunk, row in self.rows]
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:k]
```

That's the whole of vector search: score every row with `cosine`, sort, and keep the top `k`. Note
that the store knows nothing about text or models. It only sees vectors.

`Index` joins an embedder to a store, so the rest of your code can work in plain text:

```python
class Index:
    """Embeds chunks into a store, and embeds questions to search it."""

    def __init__(self, embedder, store=None):
        self.embedder = embedder
        self.store = store if store is not None else VectorStore()

    def add(self, chunks):
        self.store.add(chunks, self.embedder.embed_documents([chunk.text for chunk in chunks]))

    def search(self, question, k=5):
        return self.store.search(self.embedder.embed_query(question), k)
```

Open [code/search_handbook.py](code/search_handbook.py):

```python
documents = load_documents("workspace/handbook")
chunks = [Chunk(text, name) for name, text in documents.items()]

index = Index(OllamaEmbedder())
index.add(chunks)

for question in ["How much is the till float?", "Can I get money back for buying work footwear?"]:
    print(question)
    for hit in index.search(question, k=3):
        print(f"  {hit.score:.3f}  {hit.source}")
```

These are the two questions from section 1. **Predict:** will the second find `uniform.md` this time?

```bash
python3 search_handbook.py
```

```text
How much is the till float?
  0.747  cash-handling.md
  0.582  closing-checklist.md
  0.579  wages.md
Can I get money back for buying work footwear?
  0.676  uniform.md
  0.627  refunds.md
  0.618  expenses.md
```

Both are right, and the second is a question word search got wrong. The other two files are sensible
neighbors, too: refunds and expenses are also about money back.

Swap in the fake embedder, and only one line changes. [code/fake_search.py](code/fake_search.py) has
`Index(FakeEmbedder())` where `search_handbook.py` has `Index(OllamaEmbedder())`:

```bash
python3 fake_search.py
```

```text
How much is the till float?
  0.535  forms.md
  0.488  grinder-errors.md
  0.397  allergens.md
Can I get money back for buying work footwear?
  0.331  staff-discount.md
  0.330  food-safety.md
  0.330  branch-old-mill.md
```

The code ran the same way, and both answers are wrong. All the meaning comes from the embedding
model, and none of it from the store.

## 7. Count it

Two questions prove nothing. Chapter 18 taught you that. `questions.py` holds 22 questions with the
files that hold their answers. They were fixed before we measured anything, so nobody picked them to
flatter one side:

- **direct:** 8 questions that use the handbook's own words.
- **reworded:** 8 that avoid them, like the footwear question.
- **codes:** 6 about exact codes, like "What does E44 mean?". Two of these count either of two files.

Open [code/compare.py](code/compare.py). This loop is the core of it:

```python
for question, right in group:
    by_words = word_search(question, documents)
    names = [name for _, name in by_words]
    by_vectors = [hit.source for hit in index.search(question, k=3)]
    word_first += names[0] in right
    word_top3 += any(name in right for name in names)
    vector_first += by_vectors[0] in right
    vector_top3 += any(name in right for name in by_vectors)
    ties += names[0] in right and by_words[0][0] == by_words[1][0]
```

`in` gives `True` or `False`, and adding `True` to a number adds 1, so each line counts. `any` is
`True` if at least one item is. The last line counts word search's wins where another file had the
same score, so the alphabet chose the winner. Above the loop, `word_first = word_top3 = ... = 0` sets
all five counts to 0 in one line.

`compare.py` imports `word_search` from `word_search.py`. That file's demo sits under
`if __name__ == "__main__":`, so it doesn't run on import.

**Predict:** vector search beat word search on the footwear question. Will it win all three groups?

```bash
python3 compare.py
```

```text
Group      Questions  Words 1st  Words top 3  Vectors 1st  Vectors top 3  Tied wins
direct             8          8            8            8              8          0
reworded           8          2            2            4              5          2
codes              6          5            6            4              5          1
```

Read it group by group:

- **direct:** a draw. Both got all 8. When a question uses the document's words, word search is fine.
- **reworded:** this is the problem we started with. Vectors put the right file first 4 times, and in
  the top 3 five times. Word search got 2, and both were tied wins, so it found none outright.
- **codes:** vectors didn't win. Word search had all 6 in its top 3, and vectors had 5. (The tied win
  here was between two right files, so it's a fair one. `FN-6` reached the top 3 in a tie of its own.)

Two honest limits. First, vector search still missed half of the reworded questions as a first
result. It's better here, not solved. Second, this is 22 questions on one handbook, and a gap of one
question in a group of 6 means little. Don't read "words beat vectors on codes" from it. Read "vectors
didn't help here".

Is this like chapter 18, where the same agent scored differently each round? `same_five.py` is a
provided script that builds the index five times, and compares the top 3 for every question:

```bash
python3 same_five.py
```

```text
round 2: 22 of 22 top 3s match round 1
round 3: 22 of 22 top 3s match round 1
round 4: 22 of 22 top 3s match round 1
round 5: 22 of 22 top 3s match round 1
```

No movement. An embedding has no temperature, so nothing here is sampled. Your numbers may differ on
another machine, but they shouldn't move from run to run. So what limits this result isn't chance
between runs. It's the small number of questions.

Now read the misses. `misses.py` is provided, and it lists where the right file ranked for each
question that vectors didn't get first:

```bash
python3 misses.py
```

```text
rank  4  I'm a barista and I want to quit. How much warning do I have to give?
rank  3  I woke up feeling awful and can't make it in. How do I let my boss know?
rank  5  I found evidence of mice in the storeroom. Who handles that?
rank  4  Do I need to do anything about my ponytail at work?
rank  2  What is form IR-9 for?
rank 12  What is FN-6 used for?
```

- **`FN-6` at rank 12.** Word search only has to match the letters. An embedding gives no such
  promise, even for a code that's written in the file.
- **Mice, and the ponytail.** The mice line is in `food-safety.md`, the longest file in the handbook.
  The hair line shares `uniform.md` with shoes and aprons. A file gets one vector, so one line has to
  share it with everything else in the file. That may be why they ranked low, but we haven't tested it.
- **The quit question.** We can't say why it ranked 4th. A vector doesn't explain itself.

## 8. A score isn't an answer

What happens if the handbook has no answer? Open [code/no_answer.py](code/no_answer.py). It asks four
questions the handbook doesn't cover, then compares their scores with the top scores of the 16
questions from section 7 that vectors got right:

```python
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
```

**Predict:** will the scores for unanswerable questions be clearly lower?

```bash
python3 no_answer.py
```

```text
0.662  loyalty-card.md        What percentage does Quillon match on pension contributions?
0.659  social-media.md        Does Quillon offer dental insurance?
0.696  branch-harbour.md      What is the customer wifi password at Harbour?
0.720  branch-riverside.md    Are dogs allowed inside the Riverside branch?
16 right first hits: 7 scored below 0.720, the highest above
```

Search always returns something. It has no way to say "not here", because `search` sorts what exists
and returns the top `k`.

You might hope for a cut-off score. On this data, no cut-off works. 7 of the 16 right results scored
below the dogs question, which has no answer at all. A cut-off high enough to drop dogs would drop
those 7 too.

Look at why. `branch-riverside.md` really is the closest file to a question about the Riverside
branch. A score measures how close the *topic* is. It doesn't say the answer is in the file.

## 9. Keep the vectors

Every script so far embedded all 42 files before it could search. The vectors don't change unless the
text does, so you can save them. `VectorStore` has two more methods:

```python
def save(self, path):
    data = [{"text": chunk.text, "source": chunk.source, "vector": vector} for chunk, vector in self.rows]
    Path(path).write_text(json.dumps(data))

def load(self, path):
    data = json.loads(Path(path).read_text())
    self.rows = [(Chunk(row["text"], row["source"]), row["vector"]) for row in data]
```

It's JSON, as in chapter 02. Open [code/save_load.py](code/save_load.py). This is the second half:

```python
store = VectorStore()
store.load(SAVED)
reloaded = Index(OllamaEmbedder(), store)
hit = reloaded.search(QUESTION, k=1)[0]
print(f"{hit.score:.3f}  {hit.source}")
```

The script embeds the handbook and saves it first, so it writes `handbook_vectors.json` beside it.
`Path(SAVED).stat().st_size` is the file's size in bytes, and `:,` adds the commas.

```bash
python3 save_load.py
```

```text
saved 42 rows, 453,385 bytes
0.676  uniform.md
```

The score matches section 6. The questions still get embedded, with the same model. That part always
needs the model, and it must be the same one. Two things to remember:

- A saved vector only makes sense next to vectors from the same model.
- If a document changes, its saved vector is out of date until you embed it again.

## 10. The same methods, with Chroma

The list store compares a query with every row, and it keeps everything in memory until you save it.
That's fine for 42 files. A **vector database** is a store built for much more. It keeps its data on
disk, and it builds an index so it doesn't have to compare with every row. Chroma is one, and it runs
inside your Python, with no server to start.

42 rows is far too few to show any difference in speed, and we didn't measure one. What this section
shows is how little of your code has to change.

This section needs Chroma, and **Chroma needs Python 3.12 to 3.14**. Install it from `code`:

```bash
python3 -m pip install -r requirements-chroma.txt
```

If that fails on your Python version, read this section and skip the runs. Everything else in the
chapter, and the exercises, still work, because `whitebox` only imports Chroma inside `ChromaStore`.

```python
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
```

- `import chromadb` is inside `__init__`, not at the top of the file. Python only runs it when you
  make a `ChromaStore`, so `whitebox` still works on a machine without Chroma.
- A **collection** is Chroma's name for one set of rows, like a table.
- `"hnsw:space": "cosine"` tells it to compare by cosine.
- Every row needs a unique string `id`, so `add` counts up from the rows already there.
- `query` takes a list of queries, and returns a list of results for each, so `[0]` picks our one
  query.
- Chroma reports **distance**, where smaller is closer. Cosine distance is 1 minus cosine, so `1 -
  distance` turns it back into our score.

Open [code/search_chroma.py](code/search_chroma.py):

```python
store = ChromaStore("handbook_chroma")
index = Index(OllamaEmbedder(), store)
if store.collection.count() == 0:
    index.add(chunks)
print(f"{store.collection.count()} rows in Chroma")

for hit in index.search("Can I get money back for buying work footwear?", k=3):
    print(f"  {hit.score:.3f}  {hit.source}")
```

`Index` didn't change at all. It calls `add` and `search`, and it doesn't care what's behind them. The
store writes to a `handbook_chroma` folder, so run the script twice:

```bash
python3 search_chroma.py
python3 search_chroma.py
```

```text
42 rows in Chroma
  0.676  uniform.md
  0.627  refunds.md
  0.618  expenses.md

42 rows in Chroma
  0.676  uniform.md
  0.627  refunds.md
  0.618  expenses.md
```

The second run embedded no documents, because the 42 rows were already on disk. Is it really the same
search? `same_results.py` is provided. It runs all 22 questions through both stores:

```bash
python3 same_results.py
```

```text
same top 5, in the same order: 22 of 22
largest score difference: 0.000001
```

The stores agree. The tiny difference is rounding, because Chroma keeps its numbers at lower precision
than Python does. Chroma's index can be approximate on big collections, so don't assume this holds
for every data set. That's why the check is worth running.

So why the `if` around `add`? A database remembers. [code/chroma_twice.py](code/chroma_twice.py) leaves
the `if` out, and adds the same chunks twice. Its `shutil.rmtree` line only deletes the folder, so
each run starts empty:

```python
index.add(chunks)
index.add(chunks)

print(f"{store.collection.count()} rows")
for hit in index.search("Can I get money back for buying work footwear?", k=3):
    print(f"  {hit.score:.3f}  {hit.source}")
```

**Predict:** how many rows, and what happens to the results?

```bash
python3 chroma_twice.py
```

```text
84 rows
  0.676  uniform.md
  0.676  uniform.md
  0.627  refunds.md
```

No error. `add` simply gave the copies new ids. Now `uniform.md` fills two of your three results, and
`expenses.md` has been pushed out. Without the `if`, this is what running `search_chroma.py` twice
would do, because the rows from the first run are still there. A list store starts empty on each run,
so this is new. Exercise 3 gives you a way to clean up a result like this.

The three files these scripts leave in `code` (`handbook_vectors.json`, `handbook_chroma` and
`chroma_twice`) are safe to delete. The chapter's `.gitignore` already skips them.

## Reading errors

We triggered each of these for real, and the output is shortened.

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `whitebox.models.ModelError: Couldn't reach Ollama` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| You haven't pulled the embedding model | `whitebox.models.ModelError: Ollama said 404: {"error":"model \"nomic-embed-textt\" not found, try pulling it first"}` (we used a misspelled name to trigger it) | `ollama pull nomic-embed-text` |
| Chroma isn't installed | `ModuleNotFoundError: No module named 'chromadb'` | `python3 -m pip install -r requirements-chroma.txt` on Python 3.12 to 3.14, or use `VectorStore` |
| You called `save` on a `ChromaStore` | `AttributeError: 'ChromaStore' object has no attribute 'rows'` | Don't. Chroma is already on disk. `save` is only for the list store |
| The query came from a different embedder, in Chroma | `chromadb.errors.InvalidArgumentError: Collection expecting embedding with dimension of 768, got 64` | Use the same embedder to add and to search |

Two mistakes give no error at all, and they're worse:

- **The same wrong embedder, with the list store.** `cosine` uses `zip`, which stops at the shorter
  list. We searched the saved 768-number vectors with `FakeEmbedder`'s 64-number vector, and it ran.
  It returned `allergens.md` at 0.072 for the footwear question, which is nonsense.
- **Running from the wrong folder.** `load_documents` finds no files in a folder that isn't there, and
  returns an empty dictionary. `python3 code/search_handbook.py` from the chapter folder prints the
  two questions, and no results. Run the scripts from `code`.

## Exercises

From `chapters/19-embeddings-and-vector-search`, open [exercises.py](exercises.py) and complete the
five TODOs. Each one extends what you've built:

1. `unit`: scale a vector to length 1.
2. `above`: drop hits below a score. Section 8 showed what this can't do, but it can still clear out
   the weakest results.
3. `best_per_source`: keep the best hit from each file, which cleans up section 10's duplicates.
4. `rank_of`: find where a file ranked, as `misses.py` does.
5. `UnitStore`: your own store behind the same two methods. It stores unit vectors, so `search` only
   needs a dot product. `Index` works with it unchanged.

`super().add(...)` in TODO 5 calls the parent's method, as you did in chapter 14. The `sys.path` line at
the top of `exercises.py` is provided. It lets the file find the `whitebox` package inside `code/`.

Then check your work from `chapters/19-embeddings-and-vector-search`. These checks use `FakeEmbedder`,
so Ollama doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- **Reading a score as a percentage.** 0.7 isn't "70% relevant". Here, the lowest of 924 scores was
  0.309. Compare scores for one question, not across questions.
- **Trusting a top result.** Search always returns something, even when no file has the answer.
- **Mixing embedders.** Vectors from different models can't be compared, and the list store won't
  warn you.
- **Skipping the prefixes.** `embed_documents` and `embed_query` add them for you. Calling `embed`
  directly doesn't.
- **Adding to Chroma on every run.** It remembers. Check `count()` first.
- **Assuming vectors beat words everywhere.** They didn't on exact codes here. Measure it on your own
  questions.
- **Judging from one good question.** The footwear question looked perfect. The reworded set got 4 of 8.

## Recap

- Word search fails when a question avoids the document's words, and it fails silently.
- An embedding model turns any text into a fixed-length vector. Similar meaning gives similar vectors.
- `cosine` measures how closely two vectors point the same way.
- An `Embedder` turns text into vectors. A `VectorStore` keeps them and ranks them. An `Index` joins
  the two.
- `ChromaStore` has the same methods, so `Index` didn't change.
- Here, vectors helped most on reworded questions, and didn't help on exact codes.
- A score tells you how close a topic is. It doesn't tell you the answer is there.

## Where this comes from

The idea that a word's meaning can be learned as a vector was made popular by the 2013 paper
[Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781).
[Nomic Embed](https://arxiv.org/abs/2402.01613) describes the model you used. Chroma's `hnsw` setting
is named after the search method from
[this 2016 paper](https://arxiv.org/abs/1603.09320).

**Next:** chapter 20, where the search results go to the model, in the RAG pipeline.
