# Chapter 20: The RAG pipeline

**Time:** about 2.5 hours, plus some long evals. **You'll build:** a pipeline that finds the right passages and answers
from them, and you'll learn when you don't need one.

## Where we are

In chapter 19, you searched the handbook by meaning. You got back the right file, but not an answer.

Before you build anything to fix that, try the simplest idea there is: paste the documents into the
prompt, and ask. It works, and then it doesn't. This chapter starts there.

**RAG** stands for retrieval-augmented generation. It means: search first, put what you found in the
prompt, and let the model answer from it.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. You also need the embedding model from chapter 19. If you don't have it:

```bash
ollama pull nomic-embed-text
```

You'll work in `chapters/20-rag-pipeline/code`. This chapter doesn't use Chroma, so the plain
`VectorStore` is all you need, on any Python version.

`whitebox/rag.py` has four new pieces: `split_text`, `make_chunks`, `Rag` and `hit_rate`. Four
things are provided, and you don't need to change them:

- `workspace/records` holds a year of invented branch logs, plus supplier and product lists.
  `make_records.py` generated them, and they're already in the folder.
- `questions.py` holds 42 test questions and their checks, fixed before anything was measured.
- `library.py` has two small helpers: `all_documents` reads the handbook and the records into one
  dictionary (`|` joins two dictionaries), and `build_index` chunks and embeds them.
- `count_tokens.py`, `paste_all.py`, `hit.py`, `whole_files.py`, `hit_vs_answer.py` and `tidewater.py`
  are measuring scripts. Each section tells you what the script does and shows the part that matters,
  so you can run them without reading all of them.

To check the framework itself, run this from `code`:

```bash
python3 -m pytest tests
```

You should see `52 passed`. These tests use a fake model, so they don't need Ollama.

## 1. Paste the handbook

Open [code/paste.py](code/paste.py). `Paste` joins every document into one prompt:

```python
def run(self, question):
    text = "\n\n".join(f"[{name}]\n{body}" for name, body in self.documents.items())
    messages = [
        Message("system", RAG_SYSTEM),
        Message("user", f"Excerpts:\n\n{text}\n\nQuestion: {question}"),
    ]
    reply = self.model.chat(messages, **self.options)
    return Result(reply.content, messages + [reply], 1)
```

`RAG_SYSTEM` is the instruction you'll keep using in this chapter:

```text
Answer the question using only the excerpts below. After the answer, name the file you used in
brackets, such as [uniform.md]. If the excerpts don't contain the answer, say exactly: I don't know.
```

`run` returns a `Result`, just as an `Agent` does, so chapter 18's `run_eval` can mark it.

Now open [code/paste_try.py](code/paste_try.py). It asks two questions, prints each answer and its
`tokens_in`, and then runs three checks five times each:

```python
CASES = [
    Case("shoes", "How much is the shoe allowance?", [contains("40")]),
    Case("e44", "What does E44 mean?", [contains("dose sensor")]),
    Case("names its file", "How much is the shoe allowance?", [contains("[uniform.md]")]),
]
```

Both facts are in the handbook. **Predict:** will the model get both right?

```bash
python3 paste_try.py
```

This is real output from `qwen2.5:7b`. Long answers are cut at 160 characters by the script:

```text
Q: How much is the shoe allowance?
A: The shoe allowance is £40 every 12 months, which can be claimed using form FN-3 with a receipt.
tokens_in: 2050
Q: What does E44 mean?
A: The reference E44 is not defined in the provided documents. It's not mentioned in any of the sections related to staff policies, procedures, or guidelines. With
tokens_in: 2050
five runs each
Case                  Passed  Steps
shoes                    5/5    1.0
e44                      0/5    1.0
names its file           0/5    1.0
Total                   5/15
```

The shoe question looks perfect, 5 out of 5. If you'd stopped there, you'd think pasting just works.

But E44 is in `grinder-errors.md`, and the model said it isn't in the documents, in 5 runs of 5. And
the model was told to name its file, and it never did.

## 2. The cut you can't see

There was no error. Look at `tokens_in` instead. How big is the handbook?
[code/count_tokens.py](code/count_tokens.py) measures each file on its own, so nothing gets cut:

```python
def tokens(text):
    """Ask for one token of reply, because we only want the count of what went in."""
    return model.chat([Message("user", text)], num_predict=1).tokens_in
```

```bash
python3 count_tokens.py
```

```text
handbook    42 files   4,764 tokens
records     53 files  65,108 tokens
together    95 files  69,872 tokens
```

The handbook is 4,764 tokens, and the model received 2,050. You met this in chapter 07: when text
doesn't fit the context window, Ollama cuts it and carries on.

The window is set by an option called `num_ctx`. We didn't set it, so Ollama used its default.
`ollama ps` shows the window of a loaded model, in the `CONTEXT` column:

```text
NAME                       ID              SIZE      PROCESSOR    CONTEXT    UNTIL
qwen2.5:7b                 845dbda0ea48    4.7 GB    100% GPU     4096       4 minutes from now
```

Ours was 4,096. Yours may differ, because the default depends on your Ollama version and your
machine. So trust `tokens_in`, not this number.

Our runs tell you which end was lost. `uniform.md` is near the end of the prompt, and it survived.
`grinder-errors.md` is further forward, and it was lost. The instruction to name a file sits at the
very start, and the model stopped following it. That points to a cut from the front, with the rules
going first. Section 3 shows the same pattern.

The fix is one option. Add a number, and `paste_try.py` sets `num_ctx`:

```python
options = {"temperature": 0.7}
if len(sys.argv) > 1:
    options["num_ctx"] = int(sys.argv[1])
```

**Predict:** what will `tokens_in` be now?

```bash
python3 paste_try.py 8192
```

```text
Q: How much is the shoe allowance?
A: The shoe allowance is £40 every 12 months, according to the [uniform.md] excerpt.
tokens_in: 5080
Q: What does E44 mean?
A: E44 is a grinder error code that indicates a dose sensor fault. According to the excerpt, you should use the backup grinder and report the fault as a repair. [u
tokens_in: 5080
five runs each
Case                  Passed  Steps
shoes                    5/5    1.0
e44                      5/5    1.0
names its file           5/5    1.0
Total                  15/15
```

5 of 15 became 15 of 15, from one number. `tokens_in` is 5,080: the handbook, the instructions and
the question.

Two questions aren't much of a test. Section 9 runs all 32 handbook questions, and the cut costs far
more than you'd guess: 38/96 against 83/96.

## 3. Add the records

The handbook is small. The company also has a year of records: branch logs, suppliers and products.
Look back at the token counts. Together, they're 69,872 tokens across 95 files.

How big can the window get? Ask Ollama:

```bash
ollama show qwen2.5:7b
```

```text
    context length      32768
```

So the documents are about twice the model's limit. No value of `num_ctx` can hold them.

Open [code/paste_all.py](code/paste_all.py). It pastes all 95 files, asks eight questions once each,
and compares `tokens_in` with the size of the documents. The handbook comes first in the prompt, and
the records follow in name order, so `suppliers.md` is at the very end.

**Predict:** at the model's full 32,768 tokens, how much of the text gets in? Which questions will
pass?

```bash
python3 paste_all.py 32768
```

```text
direct:float           FAIL  'Based on the log entries, the till float appears to be recor'
direct:fridge          FAIL  'Based on the information provided in the log entries, there '
code:e44               FAIL  'Based on the context provided, E44 likely refers to a specif'
none:pension           FAIL  'Based on the information provided in the given documents, th'
records:flood          FAIL  'The log entries do not provide specific details about a floo'
records:film-crew      FAIL  'Based on the information provided, there is no specific ment'
records:fennel-min     pass  'The minimum order with Fennel Bakehouse is £60 per branch.'
records:lantern-price  pass  'The price for a 250g bag of Lantern coffee is £8.50.'

num_ctx 32768: 2/8 passed, 58 seconds per question
tokens_in 16,386 of 69,872 (23% of the text)
```

Only 16,386 tokens went in, which is half the window, and 23% of the text. It's the same pattern as
before. The two questions that passed are about `products-beans.md` and `suppliers.md`, at the end
of the prompt. Handbook facts and the early logs were lost.

Read this with care. Each question ran once, because these runs are so heavy, so treat it as a sample
and not a score. `pension` is the one to think about: the handbook doesn't say, so the right reply is
to admit it. The check only accepts the words "I don't know", and the script prints only 60
characters, so this run can't show whether that was a false failure. Our seconds came from a machine
that was busy with other work, so they say nothing about yours.

A bigger window also takes memory. `ollama ps` showed the model at 4.7 GB with a window of 4,096, and
6.6 GB with 32,768. So pasting has hit a wall: you can't fit everything, so you must choose what to
send. That's retrieval.

## 4. Cut the documents into chunks

In chapter 19, you searched whole files. A monthly log can run to about 1,000 words, and the question might
be about one sentence of it. So cut each document into smaller pieces, called **chunks**.

Open [code/whitebox/rag.py](code/whitebox/rag.py):

```python
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
```

- `re.split(r"\n\s*\n", ...)` splits the text at each blank line. `\n` is a line break, and `\s*` allows
  stray spaces between the two breaks. You don't need to know more about `re` than that.
- `current` collects paragraphs. If the next paragraph would take it past `size` words, the piece is
  finished and a new one starts.
- `len(" ".join(current).split())` counts the words collected so far.
- A paragraph is never broken. So one long paragraph can make a chunk bigger than `size`.

`make_chunks` remembers each chunk's file in `Chunk.source`, the same field you used in chapter 19.

Open [code/chunks.py](code/chunks.py). It splits a tiny text three ways, and then cuts all 95 files
at four sizes:

```python
text = "One two three.\n\nFour five six.\n\nSeven eight nine ten eleven."
print(split_text(text, size=5))
print(split_text(text, size=7))
print(split_text(text, size=100))
```

**Predict:** how many pieces will each line give? This needs no model.

```bash
python3 chunks.py
```

```text
['One two three.', 'Four five six.', 'Seven eight nine ten eleven.']
['One two three.\n\nFour five six.', 'Seven eight nine ten eleven.']
['One two three.\n\nFour five six.\n\nSeven eight nine ten eleven.']

95 files
size  20: 2980 chunks,  15 words on average
size  60:  934 chunks,  48 words on average
size 120:  447 chunks, 102 words on average
size 300:  219 chunks, 208 words on average
```

The average sits below `size`, because a piece stops before it goes over. We'll use 60 and 120.

## 5. The pipeline

Now the pieces join up. This is all of `Rag`:

```python
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
```

Compare it with `Paste.run`. There's one real change: the text in the prompt comes from a search, and
not from every document. `k` says how many chunks to send. There's no loop and no tool, and the model
is called once.

Open [code/ask.py](code/ask.py):

```python
index = build_index(all_documents(), 60)
rag = Rag(load_model(), index, k=5, options={"temperature": 0.7})

for hit in index.search(QUESTION, 5):
    print(f"{hit.score:.2f}  {hit.source}")

result = rag.run(QUESTION)
print("Answer:", result.answer)
print("tokens_in:", result.messages[-1].tokens_in)
```

It then runs two cases five times: the flood question, and a question the documents can't answer.

The flood is one sentence in a log, and `paste_all.py` missed it. **Predict:** how many tokens will
the model need now?

```bash
python3 ask.py
```

```text
0.87  log-harbour-2025-02.md
0.69  log-harbour-2025-09.md
0.68  log-harbour-2025-01.md
0.67  log-harbour-2025-02.md
0.67  log-harbour-2025-08.md
Answer: The stock worth £640 was lost when the Harbour cellar flooded. [log-harbour-2025-02.md]
tokens_in: 570
five runs each
Case                  Passed  Steps
records:flood            5/5    1.0
none:dental              5/5    1.0
Total                  10/10
```

570 tokens, against 16,386 for pasting, and the answer names its file. It fits the default window
with room to spare, so nothing is cut, and the instructions survive. The model also said "I don't
know" to the dental question in 5 runs of 5.

## 6. Measure the search alone

A wrong answer could come from the search or from the model. So measure them apart. `hit_rate`
needs no chat model:

```python
def hit_rate(index, cases, k=5):
    """The share of cases where every needed file appears in the top k. cases: (question, files)."""
    found = 0
    for question, files in cases:
        sources = {hit.source for hit in index.search(question, k)}
        found += all(name in sources for name in files)
    return found, len(cases)
```

`{... for ...}` builds a set, which is a collection with no repeats. `all(...)` is `True` only if
every file is there, so a question that needs two files counts only if both come back. `found +=`
works because Python counts `True` as 1.

Be exact about what this measures: **the right file, not the right text**. So we'll call it a **file
hit rate**.

[code/hit.py](code/hit.py) runs it on the 36 questions that have a file, for three indexes: whole
files as in chapter 19, and chunks of size 120 and 60.

**Predict:** which index will find the most files at `k=5`?

```bash
python3 hit.py
```

```text
36 questions. File hit rate, by k:
Index           k=1  k=3  k=5
whole files      21   28   31
size 120         20   24   28
size 60          25   28   28
```

Whole files win at `k=5`, 31 to 28. So why chunk at all? A number like this only tells you about the
files. The next section checks the answers.

## 7. Score the answers

Open [code/eval_all.py](code/eval_all.py). It's chapter 18's eval, on all 42 questions, three times
each. `rag60` runs twice, because you know the rule: compare a setup with itself first.

```python
indexes = {"rag60": size60, "rag60 again": size60, "rag120": size120, "whole files": whole}
for label, index in indexes.items():
    report = run_eval(Rag(model, index, 5, options), cases, runs=3, label=label)
    print(summary(report), flush=True)
    report.save(f"{label.replace(' ', '-')}.json")
```

The questions come in kinds. `direct` uses the document's words, `gap` avoids them, `code` asks about
exact codes, `hop` needs two documents, `none` has no answer, and `records` asks about the records.

**Predict:** whole files found the most files. Will they score the most? This makes 504 model calls,
so it takes a while. If your machine is slow, predict, then read our output below. You can follow the
rest of this section without running it, and section 8's script is the only one that needs its files.

```bash
python3 eval_all.py
```

```text
rag60           99/126  direct 24/24  gap 20/24  code 12/18  hop 7/18  none 18/18  records 18/24
rag60 again    100/126  direct 24/24  gap 21/24  code 12/18  hop 6/18  none 18/18  records 19/24
rag120          99/126  direct 24/24  gap 18/24  code 15/18  hop 6/18  none 18/18  records 18/24
whole files     74/126  direct 24/24  gap 17/24  code 15/18  hop 3/18  none 6/18  records 9/24
```

The most files, and the lowest score. And `rag60` against `rag120` is no contest: 99 and 100 against
99. They're as close as `rag60` is to itself, so don't pick a winner.

But is 74 fair? It should look familiar: `none` fell to 6/18, and the records to 9/24. Five whole logs
don't fit the default window. It's section 2's silent cut again.

So give whole files room. [code/whole_files.py](code/whole_files.py) runs the same eval at `num_ctx`
16384:

```bash
python3 whole_files.py
```

```text
whole 16384    103/126  direct 24/24  gap 17/24  code 15/18  hop 5/18  none 18/18  records 24/24
tokens_in: 7191
```

74 became 103, level with chunks, and records reached 24/24. We expected chunks to win here, and they
didn't. One likely reason is that a whole log keeps everything around the fact.

The honest difference is the cost. The flood question took 7,191 tokens this way, and 570 with
chunks. Whole files only worked because these files are small and we raised the window. With longer
files, five of them wouldn't fit at any setting. **On these documents, chunks bought a smaller
prompt, not a better score.**

## 8. The right file isn't the right answer

Does a file hit mean a right answer? [code/hit_vs_answer.py](code/hit_vs_answer.py) reads the two
saved `rag60` reports, and prints the questions where the file hit and the six runs disagree:

```bash
python3 hit_vs_answer.py
```

```text
Question                 File hit  Passed
mice                     yes       0/6
hair                     yes       5/6
old-mill-repair          no        6/6
card-reader              yes       0/6
tidewater-fee            yes       1/6
```

It goes wrong in both directions. `old-mill-repair` "missed" a file and still passed every time,
because the number it needed was in the file it did find. Four others found the file and still lost
runs. `card-reader` is chapter 21's problem. Let's look at the other kinds.

**A real failure.** [code/tidewater.py](code/tidewater.py) prints the chunk that holds the fee, and
runs the question five times:

```bash
python3 tidewater.py
```

```text
0.67 suppliers.md
Supplies: Machine service, Harbour and Old Mill. Account manager: Marek Dolan. Terms: Call-out fee £85. Invoices are paid within 30 days.
## Northline Service
Supplies: Machine service, Riverside and Station. Account manager: Yusuf Kaya. Terms: Call-out fee £95. Invoices are paid within 30 days.
## GreenLoop
Does this chunk say Tidewater? False
five runs
Case                  Passed  Steps
records:tidewater-fee     0/5    1.0
Total                    0/5
```

Not one of the five was right. The answer is £85, and it's right there. But the heading
`## Tidewater Espresso Service` landed at the end of the chunk before. In this chunk, the only name
near a fee is Northline. In the two saved `rag60` reports, all 5 failed runs said £95. `split_text`
doesn't know what a heading is, so the cut fell in the wrong place. The file hit rate counts this as
a success.

**A false failure.** `hair` lost one run. Here it is in `rag60.json`:

```json
{
  "run": 3,
  "failed": ["any of ['tied']"],
  "answer": "Yes, you need to tie back long hair according to the excerpt in [uniform.md]."
}
```

That answer is right. Our check wanted the word "tied", and the model wrote "tie". You saw this in
chapter 18: an eval measures its checks too. We've left the check alone, because the questions were
fixed before measuring, so that first `rag60` row is one point too low.

The `hop` questions fail for another reason: they need two facts, and `Rag` searches once.

## 9. When you don't need RAG

RAG has a cost: an index, chunk sizes to choose, and failures like the ones above. So is it always
better? [code/eval_handbook.py](code/eval_handbook.py) compares it with pasting, on the 32 handbook
questions only, where pasting can fit:

```python
setups = {
    "paste default": Paste(model, documents, options),
    "paste 8192": Paste(model, documents, {**options, "num_ctx": 8192}),
    "rag60": Rag(model, build_index(documents, 60), 5, options),
}
```

`{**options, "num_ctx": 8192}` makes a copy of the dictionary with one more key.

**Predict:** which will score highest?

```bash
python3 eval_handbook.py
```

```text
paste default   38/96  direct 14/24  gap 12/24  code 3/18  hop 9/18  none 0/12
paste 8192      83/96  direct 24/24  gap 13/24  code 18/18  hop 16/18  none 12/12
rag60           75/96  direct 24/24  gap 19/24  code 12/18  hop 8/18  none 12/12
```

Three things stand out:

- **The silent cut is the worst result here.** Same model, same text, one option: 38 against 83. With
  the default, `none` scored 0/12, because the instructions were cut along with the handbook.
- **Pasting beat RAG on this small set**, 83 to 75. It won on `code` and `hop`, because every fact
  was in front of the model and no search could miss it.
- **RAG won on `gap`**, 19 to 13. Pasting isn't simply better. Of its 11 failures there, 8 were "I
  don't know", with the answer sitting in the prompt. This is one document set, so don't take these
  gaps as general rules.

So here's how to decide:

| Your documents | What to do |
|---|---|
| Fit in the window with room to spare | Paste them. Set `num_ctx`, and check `tokens_in` |
| Too big for the window, or too big for your memory | Use RAG |
| Fit, but you ask many questions or pay per token | Weigh the cost: RAG sent 570 tokens, and pasting 5,080 |

Whichever you choose, check `tokens_in` against the size of what you meant to send. It's the only sign
of a cut you'll get.

## Reading errors

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `whitebox.models.ModelError: Couldn't reach Ollama` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| The embedding model is missing | `Ollama said 404: {"error":"model \"nomic-embed-text\" not found, try pulling it first"}` | `ollama pull nomic-embed-text` |
| You ran `hit_vs_answer.py` before `eval_all.py` | `FileNotFoundError: [Errno 2] No such file or directory: 'rag60.json'` | Run `eval_all.py` first |
| You ran `paste_all.py` with no number | `IndexError: list index out of range` | Add a window: `python3 paste_all.py 32768` |
| The text was cut | No error at all. `tokens_in` is smaller than your text | Raise `num_ctx`, or use RAG |

## Exercises

From `chapters/20-rag-pipeline`, open [exercises.py](exercises.py) and complete the five TODOs:

1. `fits_in_context`: estimate whether documents can be pasted.
2. `fixed_split`: split by word count, ignoring paragraphs.
3. `chunks_per_file`: count how many chunks each file made.
4. `cites`: a check that the answer names a file.
5. `missed`: list the questions that `hit_rate` only counts.

The `sys.path` line at the top of `exercises.py` is provided. It lets the file find the `whitebox`
package inside `code/`.

Then check your work from `chapters/20-rag-pipeline`. These checks use a fake model and a fake
embedder, so Ollama doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Optional exercise: paste everything, and report back

This one is optional, and nothing later depends on it. It's heavy for your machine, so close other
work first. We ran it on one Mac, and we'd like to know how it goes on yours.

From `code`, run `paste_all.py` with the largest window your machine can manage:

```bash
python3 paste_all.py 32768
```

On a machine with 8 GB of memory, use 16384 instead:

```bash
python3 paste_all.py 16384
```

To change the questions, edit `NAMES` at the top of the script. Use 5 to 10 names from
`questions.py`. Then compare `tokens_in` with the 69,872 tokens of text to see the cut. Run
`ollama ps` straight after, to see the memory used.

We tried 16384 on two questions only. Both failed, `tokens_in` was 8,194, which is 12% of the text,
and `ollama ps` showed 5.6 GB. The model call gives up after 180 seconds, so a slow machine may print
`no answer` for a question. That's a useful result too, so report it.

Share your result in [GitHub Discussions](https://github.com/WhiteboxAcademy/BuildAnAgentFramework/discussions):

```text
Machine:
Memory:
num_ctx:
Score:
Seconds per question:
tokens_in:
```

## Common mistakes

- **Trusting a good answer as proof nothing was cut.** The shoe question passed 5 of 5 with most of
  the handbook missing. Check `tokens_in`.
- **Reaching for RAG before you need it.** If the documents fit, pasting is less work, and it scored
  higher on our handbook.
- **Reading a file hit rate as a success rate.** The best file hit rate here came with the worst
  score.
- **Blaming the search for a cut.** Whole files looked terrible until they had room.
- **Picking a chunk size from one run.** `rag60` and `rag120` were as close as `rag60` and itself.
- **Forgetting the model has to read the chunk.** A chunk with no name in it can give a confident
  wrong answer.

## Recap

- Pasting works if the text fits. If it doesn't, Ollama cuts it from the front with no error, and
  your instructions can go too.
- `num_ctx` sets the window, and `tokens_in` shows what really went in.
- `split_text` and `make_chunks` cut documents into pieces, at paragraph breaks.
- `Rag` searches once, puts the hits in the prompt, and asks the model once.
- `hit_rate` is a file hit rate: right file, not right text. Measure the answers as well.
- On our documents, chunks bought a much smaller prompt, not a better score.
- If your documents fit, you may not need RAG.

## Where this comes from

The name and the idea come from the 2020 paper
[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401).

**Next:** chapter 21, where you'll repair what chunking lost, and measure the fix.
