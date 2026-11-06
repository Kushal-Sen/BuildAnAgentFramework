# Chapter 23: Agentic RAG

**Time:** about 2.5 hours. The long eval is optional. **You'll build:** an agent that searches for
itself, and you'll measure what that really buys, and what to do where it falls short.

## Where we are

In chapters 21 and 22, you improved retrieval. Titles, keyword search and hybrid search each helped
some questions, and you learned not to rank scores that sit close together.

One kind of question hardly moved: `hop`. These need a second fact. "How much notice must a shift
lead give?" needs the shift lead's band, and then the rule for that band. Every setup so far searches
once, with the question as it was typed.

This chapter hands the search to the agent. It's the last chapter of Part 4, and it has the biggest
gain of the part. It also has a surprise: the agent's gain doesn't come from where we expected.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. You also need the embedding model from chapter 19. If you don't have it:

```bash
ollama pull nomic-embed-text
```

You'll work in `chapters/23-agentic-rag/code`. This chapter doesn't use Chroma, so any Python version
works.

`whitebox/rag.py` has two new pieces: `search_tool` and `AGENT_SYSTEM`. These things are provided, and
you don't need to change them:

- `questions.py` holds the same 42 questions as before, with the two corrected checks from chapters 21
  and 22. Section 8 adds a stricter hop check to this file.
- `library.py` has the helpers you know: `all_documents`, `build_index`, `build_hybrid` and `Remember`.
  Titles are on by default here. It adds `build_agent`, explained in section 3, three small functions
  that read a run (`searches`, `tool_text` and `files_seen`), and `Keep`, explained in section 5.
- `results/` holds our saved runs of this chapter's evals. A script that reads results uses your own
  file if you've made one, and ours if you haven't. So **you can follow the whole chapter without the
  long eval.**
- `more_hits.py`, `two_parts.py`, `cost.py`, `failures.py`, `hop_audit.py`, `rescore.py` and `fair.py` are
  measuring scripts. Each section says what the script does and shows the part that matters.

**A map of the setup names.** All of them use the same 95 files:

| Name | What it is |
|---|---|
| `titles60`, `titles120` | Chapter 21's `Rag`, with titles, on chunks of about 60 or 120 words |
| `hybrid60` | Chapter 22's `Rag`, with hybrid search |
| `agent60`, `agent-hybrid60` | This chapter's agent, on those two kinds of index |
| `-again` | The same setup, run a second time |

Chapter 20 called `Rag` without titles `rag60`. Chapter 21 renamed that `plain60`, so here every name
says what's in it.

To check the framework itself, run this from `code`:

```bash
python3 -m pytest tests
```

You should see `59 passed`. These tests use a fake model, so they don't need Ollama.

## 1. One search isn't enough

Open [code/one_shot.py](code/one_shot.py). It's chapter 20's pipeline with chapter 21's titles:

```python
index = build_index(all_documents(), 60)
rag = Rag(load_model(), index, k=5, options=OPTIONS)

for hit in index.search(QUESTION, 5):
    print(f"{hit.score:.2f}  {hit.source}")

print("Answer:", rag.run(QUESTION).answer)
```

The question is "I'm a shift lead. How much notice must I give when I resign?" The handbook has two
facts you need. `pay-bands.md` says a shift lead is Band C. `resignation.md` says Band C gives 4 weeks.

**Predict:** will one search find both?

```bash
python3 one_shot.py
```

This is real output from `qwen2.5:7b`:

```text
0.76  resignation.md
0.71  breaks-and-staff-drinks.md
0.69  shifts.md
0.68  rota-swaps.md
0.68  flexible-working.md
Answer: You must give 8 weeks' notice when you resign as a Band E staff member. [resignation.md]
five runs
Case                  Passed  Steps
hop:lead-notice          0/5    1.0
Total                    0/5
```

The search found the rule, and not the band. So the model made a band up. It's a confident answer
that cites a real file, and it's wrong in 5 runs of 5.

## 2. Would more hits help?

The obvious fix is to raise `k`. [code/more_hits.py](code/more_hits.py) finds where `pay-bands.md`
ranks, and then tries bigger values:

```python
hits = index.search(QUESTION, 934)  # All the chunks, in order.
rank = next(number for number, hit in enumerate(hits, start=1) if hit.source == "pay-bands.md")
```

`next(... for ...)` gives you the first item that matches, and stops looking. The rest of the script
runs the same question five times at each `k`, and uses `Keep` from `library.py` to remember each run.

**Predict:** where will `pay-bands.md` rank?

```bash
python3 more_hits.py
```

Answers are cut at 110 characters by the script:

```text
pay-bands.md first appears at rank 134 of 934
k=5    passed 0/5  tokens_in 423
k=10   passed 0/5  tokens_in 732
k=20   passed 0/5  tokens_in 1465
k=134  passed 0/5  tokens_in 2050
 - The policy for resignation notice periods is not detailed in the provided logs, tips, closing checklist, suppl
 - Based on the provided information and common practices in retail and hospitality, shift leads are typically ex
 - Based on the information provided in the "Job roles and bands" document, there isn't specific guidance on noti
 - Based on the information provided in the `pay-bands.md` document, the role of Shift Lead falls under Band C. H
 - Based on the job roles and bands provided, there is no specific information given about the notice period for
```

Rank 134. That makes sense: `pay-bands.md` is about roles, and the question is about resigning.
Nothing in the question points at it except "shift lead".

And look at the last `tokens_in`. You know that number from chapter 20: 2,050 is the silent cut. At
`k=134`, most of the prompt was thrown away, instructions first, and the answers stopped following
them. An earlier run of this script passed 2 of 5 at `k=134`, so don't read much into 0, but it's no
fix either way. Raising `k` can't do this job. Something has to look up the band.

## 3. Give the agent the search

You built an agent in Part 2, and it can call tools. So make the search a tool. Here's all of
`search_tool`, in [code/whitebox/rag.py](code/whitebox/rag.py):

```python
def search_tool(index, k=3):
    """Turn an index into a tool, so an agent can decide what to look up."""

    @tool
    def search_handbook(query: Annotated[str, "What to look up, in a few words"]) -> str:
        """Search the staff handbook. Search again with new words if the result isn't enough."""
        return excerpts(index.search(query, k)) or "Nothing found."

    return search_handbook
```

- `@tool` is the decorator from chapter 14. The docstring and the `Annotated` text are what the model
  reads, so they're the instructions for this tool.
- `search_handbook` is defined inside `search_tool`, so it can use `index` and `k` after `search_tool`
  has returned. Python keeps them for it. That's how each tool gets its own index.
- `excerpts` is the function `Rag` uses, so the model sees the same `[file.md]` format.
- It works with any object that has `search`: `Index`, `KeywordIndex`, `HybridIndex` or `Reranker`.

`AGENT_SYSTEM` tells the agent how to use it:

```text
You answer questions about the Quillon Coffee staff handbook. Use search_handbook to find facts, and
never answer from memory. One search may not be enough: if an answer depends on a second fact, such
as a band or a branch's contractor, search for that too. After the answer, name the file you used in
brackets, such as [uniform.md]. If searching doesn't find the answer, say exactly: I don't know.
```

Notice what changed from `Rag`. There, your code searched, using the question as typed. Here, the
**model** writes the query, and the model decides whether to search again. Nothing in the loop is
new. It's chapter 12's loop, with a tool that happens to be a search.

`build_agent` in `library.py` puts it together, with chapter 17's safety nets:

```python
def build_agent(model, index, k=3):
    return Agent(
        Retry(RescueToolCalls(model)),
        Toolbox([search_tool(index, k)]),
        system=AGENT_SYSTEM,
        options=OPTIONS,
        hooks=[LoopGuard()],
    )
```

`k` is 3 here, and 5 in `Rag`. Each search brings back less, because the agent can search again.

## 4. What did it search for?

[code/agent_ask.py](code/agent_ask.py) asks the same question, and prints every query the agent chose:

```python
result = agent.run(QUESTION)
for number, query in enumerate(searches(result), start=1):
    print(f"search {number}: {query}")
print("Files seen:", ", ".join(files_seen(tool_text(result))))
print("Answer:", result.answer)
print("Model calls:", result.steps)
```

The system prompt even names this case: "such as a band". **Predict:** what will it search for, and
how many times?

```bash
python3 agent_ask.py
```

```text
search 1: shift lead resignation notice period
Files seen: breaks-and-staff-drinks.md, resignation.md, shifts.md
Answer: As a shift lead, if you are in Band C or Band D, you must give 4 weeks' notice when resigning. If you are in Band E, you need to give 8 weeks' notice. [resignation.md]
Model calls: 2
```

We expected a second search for the band. There wasn't one. The agent did rewrite the question into a
tidy query, but then it stopped, and it hedged across bands.

One run proves little, so [code/two_parts.py](code/two_parts.py) runs it five times. It also asks a
version that spells out both parts, to see whether the agent can do this when the need is obvious:

```python
QUESTIONS = [
    "I'm a shift lead. How much notice must I give when I resign?",
    "What band is a shift lead, and how much notice must that band give when they resign?",
]
```

```bash
python3 two_parts.py
```

```text
I'm a shift lead. How much notice must I give when I resign?
  searches 1  both files False  only 4 weeks False  ['shift lead resignation notice period']
  searches 1  both files False  only 4 weeks False  ['shift lead resignation notice period']
  searches 1  both files False  only 4 weeks False  ['shift lead resignation notice period']
  searches 1  both files False  only 4 weeks False  ['shift lead resignation notice period']
  searches 1  both files False  only 4 weeks False  ['shift lead resignation notice period']
What band is a shift lead, and how much notice must that band give when they resign?
  searches 1  both files False  only 4 weeks False  ['shift lead band resignation notice period']
  searches 1  both files True   only 4 weeks True   ['shift lead band resignation notice']
  searches 1  both files False  only 4 weeks False  ['shift lead band resignation notice period']
  searches 1  both files True   only 4 weeks True   ['shift lead band resignation notice']
  searches 1  both files False  only 4 weeks True   ['shift lead band resignation notice period']
```

`only 4 weeks` means the answer gives 4 weeks and no other period. As asked, it never did, in 5 runs
of 5. Spelled out, it did 3 times. And look at how: the word "band" went into the same query. An
earlier run of the script found both files in 4 of 5. Either way, **all 10 runs made one search.**

So the loop can search twice, but this 7B model rarely decides to. Keep that in mind when you see the
scores.

## 5. Measure it

[code/eval_agent.py](code/eval_agent.py) is the eval from chapters 20 and 21. It runs each setup on all
42 questions, three times each, with titles on. The two agents each run twice, and so does `titles60`,
because you know the rule: compare a setup with itself first.

```python
for label in sys.argv[1:]:
    keep = Keep(SETUPS[label]())
    report = run_eval(keep, cases, runs=3, label=label)
    print(summary(report), flush=True)
    report.save(f"{label}.json")
    keep.save(f"{label}-runs.json")
```

A `Report` only saves failed answers, and no queries. `Keep` is a small wrapper with a `run` method, so
`run_eval` can't tell it from an agent. It records what each run searched for, what came back, its
answer and its token count, and writes them to `<label>-runs.json`. Everything after this section reads
those files, so it needs no model.

**Predict:** will letting the agent search beat every one-shot setup?

The full run is about 1,500 model calls, and it takes a long while, so you don't have to do it. To see
it work, run two setups. That's about 380 calls:

```bash
python3 eval_agent.py titles60 agent60
```

Here's our full run, from `results/`:

```text
titles60               97/126  direct 24/24  gap 18/24  code 12/18  hop 4/18  none 18/18  records 21/24
titles60-again         98/126  direct 24/24  gap 18/24  code 12/18  hop 5/18  none 18/18  records 21/24
titles120             105/126  direct 24/24  gap 19/24  code 15/18  hop 5/18  none 18/18  records 24/24
hybrid60              102/126  direct 24/24  gap 21/24  code 15/18  hop 3/18  none 18/18  records 21/24
agent60               112/126  direct 24/24  gap 23/24  code 13/18  hop 12/18  none 16/18  records 24/24
agent60-again         115/126  direct 24/24  gap 24/24  code 12/18  hop 15/18  none 17/18  records 23/24
agent-hybrid60        119/126  direct 24/24  gap 22/24  code 18/18  hop 13/18  none 18/18  records 24/24
agent-hybrid60-again  117/126  direct 24/24  gap 23/24  code 17/18  hop 14/18  none 15/18  records 24/24
```

Every agent row beats every one-shot row. The smallest gap is 7 points, 112 against 105, and an agent
differs from itself by up to 3. That's the clearest gain in Part 4.

What not to conclude:

- **Don't rank the two agents.** 112 to 115 and 117 to 119 are too close, with six runs per question.
  One thing does stand out: `code` is 17 or 18 of 18 with hybrid search, and 12 or 13 without it,
  because exact identifiers are what keyword search is for.
- **Don't rank the one-shot rows either.** `titles120` is ahead here, by about as much as chapters 21
  and 22 told you not to trust.
- We didn't rerun `Reranker`. It's slow, and chapter 22 covers it. So this table says nothing new
  about it.

And `hop` looks solved, at 12 to 15 of 18. After section 4, that should make you suspicious.

## 6. What it cost

[code/cost.py](code/cost.py) reads the saved runs. It needs no model:

```bash
python3 cost.py
```

```text
Setup                   Calls  Tokens in  Stopped   (calls and tokens per question)
titles60                 1.00        509        0
titles60-again           1.00        509        0
titles120                1.00        811        0
hybrid60                 1.00        473        0
agent60                  2.06        874        0
agent60-again            2.12        965        0
agent-hybrid60           2.02        808        0
agent-hybrid60-again     2.10        905        1

agent60, both runs: how many searches did each run make?
Kind       Runs  None   One  More
direct       48     0    48     0
gap          48     0    47     1
code         36     0    34     2
hop          36     0    33     3
none         36     0    33     3
records      48     0    48     0
```

So the gain isn't free. An agent makes about twice the model calls, because it needs one call to
choose the search and one to answer. Tokens rise too, from about 500 to about 900. That's about
what `titles120` costs, so a bigger chunk spends a similar number of tokens. We make no claim about seconds here, because the machine was shared.
Count calls and tokens on your own runs, and time them yourself.

Now the bottom table. The agent never skipped the search, which is what "never answer from memory"
asked for. But it searched more than once in **9 runs of 252**. On `hop`, the questions it was built
for, only 3 runs of 36 searched again.

`python3 failures.py again` lists those nine:

```text
e44               pass  ['E44', 'E44', 'E44']
riverside-repair  pass  ['Riverside espresso machine broken contact', 'Riverside espresso machine contact number']
riverside-repair  pass  ['Riverside espresso machine broken number', 'Riverside espresso machine repair number']
pension           FAIL  ['pension contribution match percentage', 'pension match contribution percentage', 'pension contribution match percentage']
scald             pass  ['steam wand hand injury procedure', 'hand scalded under tap duration']
e44               pass  ['E44', 'E44', 'E44']
riverside-repair  pass  ['Riverside espresso machine broken contact', 'Riverside espresso machine contractor contact number']
pension           pass  ['pension contribution match percentage', 'pension match contribution percentage', 'pension contribution match percentage']
dogs              FAIL  ['Riverside branch pet policy', 'pet policy dog', 'pet policy']
```

The script prints the first three queries of each. Read them. Almost all retry the same search with
slightly different words. None of them takes a fact from the first result and looks up what it needs
next. `scald` comes closest. The idea of "find the band, then find the rule" doesn't appear once.

## 7. Is it the loop, or the query?

If the agent nearly always searches once, why did it score higher? There are three differences from
`titles60`: the query, the `k`, and the system prompt. [code/replay.py](code/replay.py) separates the
first two from the last. It gives plain `Rag`, with `RAG_SYSTEM` and one model call, the exact query
the agent chose for that run, at the agent's `k=3`:

```python
class AgentQueries:
    """Searches for the agent's first query in place of the question. Each run uses the next saved one."""

    def __init__(self, index, runs):
        self.index = index
        self.queries = {}
        for run in runs:
            self.queries.setdefault(run["question"], []).append(run["searches"][0])

    def search(self, question, k=5):
        return self.index.search(self.queries[question].pop(0), k)
```

`setdefault` gets a key's list, and creates an empty one first if the key is new. `pop(0)` removes the
first item and returns it, so each run uses the next query. Because `AgentQueries` has a `search`
method, `Rag` accepts it as an index.

**Predict:** the search is now the same as the agent's. Will the score be?

```bash
python3 replay.py
```

```text
replay                101/126  direct 24/24  gap 20/24  code 12/18  hop 3/18  none 18/18  records 24/24
```

A first run scored 102, so call it level. That's about 4 points above `titles60`, and it's the query's
work. `gap` and `records` rose, with no loop at all: a short query beats a chatty question. It's still
11 below `agent60`, though, and most of that is `hop`: 3 against 12. So what's in those hop passes?

## 8. Read the hop passes

You've seen the answers to `lead-notice`. "Band A and B give 2 weeks, Band C and D give 4 weeks, Band E
gives 8 weeks" contains "4 weeks", so it passes. It's also not an answer.

Chapter 18 said an eval measures its checks too. So here's a stricter check, now in `questions.py`.
The answer must say the right value, and mustn't also say the wrong ones:

```python
STRICT = {
    "harbour-arrive": (["06:00", " 6:00", "6 am", "6am"], []),
    "senior-beans": (["25%"], ["15%", "30%"]),
    "riverside-repair": (["0300 555 0177"], ["0300 555 0142"]),
    "shift-lead-pay": (["14.75"], ["12.60", "16.90"]),
    "lead-notice": (["4 weeks", "four weeks"], ["2 weeks", "8 weeks"]),
    "old-mill-repair": (["0300 555 0142"], ["0300 555 0177"]),
}
```

This check came after we read the answers, so it isn't a fixed test like the original 42. Treat it as
a way of reading these runs. [code/hop_audit.py](code/hop_audit.py) counts both checks, and whether
both needed files ever came back:

```bash
python3 hop_audit.py
```

```text
agent60 + agent60-again
Question           Runs  Loose  Strict  Both files  Searched again
harbour-arrive        6      3       0           0               0
senior-beans          6      2       2           0               0
riverside-repair      6      6       6           0               3
shift-lead-pay        6      5       0           0               0
lead-notice           6      5       0           0               0
old-mill-repair       6      6       6           0               0
Total                36     27      14           0

agent-hybrid60 + agent-hybrid60-again
Question           Runs  Loose  Strict  Both files  Searched again
harbour-arrive        6      1       0           0               0
senior-beans          6      4       4           0               0
riverside-repair      6      5       5           5               0
shift-lead-pay        6      5       0           0               0
lead-notice           6      6       1           0               0
old-mill-repair       6      6       6           0               0
Total                36     27      16           5
```

Take the questions in two groups.

**`riverside-repair` and `old-mill-repair` pass, 23 of 24.** But each branch file holds the contractor's
number, so one file is enough. These two aren't really hop questions, and we only learned that here.
Here the loop did earn something, though. In `agent60`, 3 of 6 `riverside-repair` runs searched again.
In all three, the first query missed the number, and the second one found it. So searching again helps
when the first words miss. It's just rare. `replay` scored 0 of 3 on this question, but one of its
three searches did hold the number, so the prompt plays a part too.

**The other four really need two files, and no agent run saw both: 0 of 48.** They passed the strict
check 7 times of 48, without the second fact. `senior-beans` said 25% six times with `pay-bands.md`
never in front of it, so that's a lucky pick, or a guess from the word "senior". The other "passes"
were false:

- `lead-notice` and `shift-lead-pay` listed every band and let the reader choose.
- `harbour-arrive` is a bug in our check. The answer "between 06:30 and 16:00" contains `6:00`, inside
  `16:00`. The right answer is 06:00, and no run gave it.

[code/rescore.py](code/rescore.py) applies the strict hop check to every setup:

```bash
python3 rescore.py
```

```text
Setup                      Old  Old hop   Strict  Strict hop
titles60                97/126     4/18   96/126        3/18
titles60-again          98/126     5/18   96/126        3/18
titles120              105/126     5/18  102/126        2/18
hybrid60               102/126     3/18  102/126        3/18
replay                 101/126     3/18  101/126        3/18
agent60                112/126    12/18  107/126        7/18
agent60-again          115/126    15/18  107/126        7/18
agent-hybrid60         119/126    13/18  114/126        8/18
agent-hybrid60-again   117/126    14/18  111/126        8/18
```

The agents still lead every one-shot row. The smallest gap falls from 7 to 5 points. So the gain is
real, and most of it holds up. But hop drops to 7 or 8 of 18, and most of that is the two questions
that didn't need a hop. **The agent didn't solve multi-hop questions.** On this model, it made them
look solved.

Here are the failures, from `python3 failures.py hop`:

```text
senior-beans (agent60), 1 searches: senior barista discount retail beans
    According to the staff handbook, a senior barista, which I assume is a Band E, gets 30% off retail beans when off shift and using a staff card.  [staff-discount.md]
shift-lead-pay (agent60), 1 searches: hourly rate shift lead
    The hourly rate for a shift lead is not explicitly stated, but based on the information provided, shift leads are likely Band D, with an hourly rate of £16.90. [wages.md]
lead-notice (agent60), 1 searches: shift lead resignation notice period
    As a shift lead, if you are a Band E staff member, you must give 8 weeks' notice when you resign. [resignation.md]
```

We've picked three of the nine. Each search was good, and it found the right rule. The band was the
missing piece, and the model had a tool that could fetch it. It wrote "I assume", "likely" and "if you
are" instead. Band E isn't the shift lead's band, and 8 weeks is twice the right answer. The search
was fine, and the answer was bad. That's the failure to look for: the model papers over a gap instead
of searching.

## 9. Does it know when to stop?

One-shot setups scored 18/18 on `none`. The agents scored 15 to 18. Did searching make them answer
questions they should decline? `python3 failures.py none` prints all six failures, in 72 runs:

```text
pension (agent60), 3 searches: pension contribution match percentage
    I've searched the handbook multiple times, but I couldn't find any information about the percentage that Quillon matches on pension contributions.   [log-old-mill-2025-04.md] [log-old-mill-2025-12.md] [log-riverside-2025-03.md]
dogs (agent60), 1 searches: Riverside branch pet policy
    I couldn't find any specific pet policy mentioned in the logs for the Riverside branch. The logs do not provide information about allowing dogs inside the branch. I would recommend checking the current staff handbook or contacting the branch directly for the most accura
dogs (agent60-again), 6 searches: Riverside branch pet policy
    I don't see any specific mention of allowing dogs or pets in the handbook. The section [food-safety.md] focuses on pest control and food safety, not on visitor policies.  Given the lack of specific information, it seems that dogs are not allowed inside the Riverside bra
pension (agent-hybrid60-again), 8 searches: pension contribution match percentage
    Stopped: no answer after 8 steps.
dogs (agent-hybrid60-again), 1 searches: Riverside branch dog policy
    I couldn't find any specific policy regarding dogs in the Riverside branch. The logs do not mention any such rules or exceptions. You might want to check directly with the branch manager, Sam Achebe, or the equipment service contractor, Northline Service, for the most a
records-none (agent-hybrid60-again), 1 searches: health inspector Station branch 2025 score
    I couldn't find a direct mention of the health inspector's score for the Station branch in 2025. The logs I found do not contain that information. [log-station-2025-12.md] and [log-station-2025-05.md] do not include any health inspection records.   Would you like to try
```

Read them one by one:

- **Four are declines in other words.** "I couldn't find any..." is the right behaviour. The check wants
  the exact words "I don't know", so these are false failures, or at worst not following the format.
- **One ran out of steps.** `pension` searched eight times and hit `max_steps`. It gave no wrong answer,
  and no answer at all, and it used 8 model calls to get there. Chapter 17's `LoopGuard` only blocks
  exact repeats, and the model kept changing the words.
- **One really answered.** After six searches, the agent decided "it seems that dogs are not allowed".
  The handbook doesn't say that. Nothing in the documents supports it: the agent turned "I found
  nothing" into a rule.

That's 1 run in 72. It's rare, but it's the worst kind of failure here, because it reads like a
policy. And `Rag` never did it, on these runs.

## 10. Can we force the second search?

So far, the agent could search twice and didn't. Before you accept that, try to fix it. There are three
attempts in [code/fixes.py](code/fixes.py), and each one changes something different. Each runs on the six hop
questions, five times, and `hop_fixes.py` prints the same columns as `hop_audit.py`.

**Attempt 1: tell it harder.** `CHECK_SYSTEM` adds this to the agent's system prompt:

```text
Before you answer, ask: does the rule I found depend on something I haven't looked up yet, such as
which band a role is in? If it does, search for that first. Never guess it, and never list every option.
```

**Predict:** how many of the 30 runs will see both files?

```bash
python3 hop_fixes.py check
```

```text
Question           Runs  Loose  Strict  Both files
harbour-arrive        5      1       1           0
senior-beans          5      1       1           0
riverside-repair      5      4       4           1
shift-lead-pay        5      3       0           0
lead-notice           5      5       0           0
old-mill-repair       5      3       3           0
Total                30     17       9           1
```

One. The prompt names this exact case, and the model still doesn't do it.

**Attempt 2: ask what's missing.** Maybe the model will spot the gap if you stop and ask. `AskMissing`
searches once, then makes a separate model call: is a fact missing? Reply with a search query, or `NONE`.

```bash
python3 hop_fixes.py missing
```

```text
Question           Runs  Loose  Strict  Both files
harbour-arrive        5      0       0           0
senior-beans          5      1       1           1
riverside-repair      5      0       0           0
shift-lead-pay        5      0       0           0
lead-notice           5      1       1           0
old-mill-repair       5      5       5           0
Total                30      7       7           1
```

Worse. The model nearly always replies `NONE`. It can't see what isn't there, even when you ask.

**Attempt 3: don't ask whether, ask what.** Both attempts left the choice to the model, and the model
doesn't choose to search again. So take the choice away. `Split` asks for the facts *before* any
search, then your code always searches for each one:

```python
class Split:
    """Ask for the facts first, always search for each one, and answer once."""

    def __init__(self, model, index, k=3, options=None):
        self.model, self.index, self.k, self.options = model, index, k, options or {}

    def run(self, question):
        asked = [Message("user", ASK_FACTS.format(question=question))]
        reply = self.model.chat(asked, **self.options)
        queries = [line.strip(' -*"0123456789.') for line in reply.content.splitlines() if line.strip()][:3]
        hits = []
        for query in queries:
            hits = add_new(hits, self.index.search(query, self.k))
        return answer_from(self.model, question, hits, asked + [reply], queries, self.options)
```

- `ASK_FACTS` asks for one short search query per fact, one per line, and at most 3.
- `splitlines()` makes a list of the reply's lines, and `strip` removes any numbers or bullets the model
  added. `[:3]` keeps the first three.
- `add_new` joins the hits, leaving out any you already have. `answer_from` is one more model call,
  with `RAG_SYSTEM` and one added line: don't list every option.

There's no agent and no tool here. It's two model calls, with your code in charge of the searching.

```bash
python3 hop_fixes.py split
```

```text
Question           Runs  Loose  Strict  Both files
harbour-arrive        5      2       1           2
senior-beans          5      1       1           0
riverside-repair      5      1       1           1
shift-lead-pay        5      4       4           4
lead-notice           5      1       1           1
old-mill-repair       5      3       3           3
Total                30     12      11          11
```

Both files came back in 11 runs, and look at the last two columns: they nearly match. Now a pass comes
from having the facts, and the loose and strict counts agree.

Thirty runs is small, so measure it on everything. `split60` is in `eval_agent.py`, and it's saved in
`results/`, run twice as usual:

```bash
python3 rescore.py split60 split60-again
python3 hop_audit.py split60 split60-again
```

```text
Setup                      Old  Old hop   Strict  Strict hop
split60                105/126     5/18  105/126        5/18
split60-again          106/126     4/18  106/126        4/18

split60 + split60-again
Question           Runs  Loose  Strict  Both files  Searched again
harbour-arrive        6      2       2           5               6
senior-beans          6      0       0           2               6
riverside-repair      6      0       0           0               6
shift-lead-pay        6      2       2           2               3
lead-notice           6      3       3           3               6
old-mill-repair       6      2       2           0               6
Total                36      9       9          12
```

Read it carefully, because it's a mixed result:

- **Overall, it didn't beat the agents.** Strict scores of 105 and 106, against 107 to 114 for agents and
  96 to 102 for one search. It costs 2 model calls, as an agent does, and about 630 tokens.
- **On the four real hop questions, it did something new.** Both files came back in 12 of 24 runs. For
  the agents, it was 0 of 48. All 7 of its strict passes on those questions came from those 12 runs. The
  agents also passed 7 times, of 48, without ever seeing both files.
- **It lost the repair questions.** The number was in the hits in all 12 of those runs, and the model
  still said "I don't know", often naming the right file. `replay`, with the same `RAG_SYSTEM` rule, also
  failed `riverside-repair`. We didn't test why. So the search was right and the answer was wrong, and
  that's why its hop total is lower than the agents'.
- **It missed both files half the time.** When its queries don't name the right fact, the search can't
  help.

Be careful with this one too. We wrote `ASK_FACTS` after reading these failures, and its example ("what
group that job is in") looks a lot like our questions. So it may do worse on questions it wasn't written
for. It's a direction, not a result.

The lesson is about who decides. This model won't choose a second search, whatever you tell it. If your
task needs one, put that step in your code. Exercise 6 gives you `ASK_FACTS` to improve.

## 11. A fair comparison

We've compared the agent with one-shot setups at the default window. Those aren't the only options.
[code/fair.py](code/fair.py) puts chapter 20's best results beside them, from the output saved there:

```bash
python3 fair.py
```

```text
Chapter 20, whole files with num_ctx 16384, all 42 questions:
$ python3 whole_files.py
whole 16384    103/126  direct 24/24  gap 17/24  code 15/18  hop 5/18  none 18/18  records 24/24
tokens_in: 7191

Chapter 20, handbook pasted with num_ctx 8192, 32 handbook questions:
$ python3 eval_handbook.py
paste default   38/96  direct 14/24  gap 12/24  code 3/18  hop 9/18  none 0/12
paste 8192      83/96  direct 24/24  gap 13/24  code 18/18  hop 16/18  none 12/12
rag60           75/96  direct 24/24  gap 19/24  code 12/18  hop 8/18  none 12/12
```

We didn't rerun these. They use chapter 20's old `hair` check and its loose hop check, and a large
window. So they're only a rough guide. Still:

- **Whole files with a big window scored 103/126.** That's level with our one-shot rows, with a single
  model call. The agents scored higher here, but it's a claim about these setups on these documents.
  We haven't shown that agents beat everything you could build.
- **Pasting the handbook scored `hop` 16/18**, against the agents' loose 12 to 15. When both facts are in
  front of the model, it can often join them. So if your documents fit, pasting may still be the best
  answer to a multi-hop question. Those 16 came from the loose check, so some may be false too.

So the choice isn't "agents are better". It's a set of trade-offs:

| Your situation | What to try |
|---|---|
| Documents fit in the window | Paste them, and set `num_ctx` |
| Too big to paste, and simple questions | `Rag` is one call and easy to reason about |
| People ask in their own words | Rewrite the query first. `replay` gained about 4 points with no loop, though writing a query takes a model call |
| You can afford about twice the calls | An agent with `search_tool` scored highest here |
| The answer needs a chain of facts | Search for each fact in your code, as `Split` does, and read the answers. Nothing here solved it |

A bigger model may well plan a second search. We tested one 7B model, on one document set, and this
chapter's results are about that.

## Reading errors

The first two are the errors you met in chapter 20. We triggered the others for real.

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `whitebox.models.ModelError: Couldn't reach Ollama` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| The embedding model is missing | `Ollama said 404: {"error":"model \"nomic-embed-text\" not found, try pulling it first"}` | `ollama pull nomic-embed-text` |
| You ran `failures.py` with no word | `IndexError: list index out of range` | Add one: `python3 failures.py hop` |
| You named a fix that doesn't exist | `KeyError: 'splits'` | Use `check`, `missing` or `split` |
| The agent never finished | No error. The answer is `Stopped: no answer after 8 steps.` | Read its searches. It's `max_steps` working as planned |

## Exercises

From `chapters/23-agentic-rag`, open [exercises.py](exercises.py) and complete the five TODOs:

1. `searched_for`: a check that the agent searched for a word.
2. `found_files`: a check that the needed files came back.
3. `diagnose`: say whether a run was right, or missed in the search, or answered badly.
4. `calls_per_question`: the cost of a setup, from a `Report`.
5. `SearchBudget`: a hook that limits searches, so `pension` can't use eight.

The `sys.path` line at the top of `exercises.py` is provided. It lets the file find the `whitebox`
package inside `code/`.

Then check your work from `chapters/23-agentic-rag`. These checks use a fake model and a fake embedder,
so Ollama doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

**Exercise 6, optional: beat `Split`.** Change `ASK_FACTS` in `code/fixes.py`, and run
`python3 hop_fixes.py split`. Try removing the example first, and see what it was doing. There's no worked
answer, because we don't have one. Watch the `Both files` column, then check the other questions with
`python3 eval_agent.py split60`, because a prompt that helps here can hurt elsewhere.

## Part 4 checkpoint

You've finished Part 4. Before moving on, complete the
[Part 4 checkpoint](../../checkpoints/part-4/README.md), a library guide searched two ways, and
measured, using everything from chapters 19 to 23.

## Common mistakes

- **Leaving a required step to the model.** If a task needs a second search, put it in your code.
- **Assuming the loop means the agent will use it.** The tool said "search again", and so did the
  prompt. It did so in 9 runs of 252.
- **Believing a pass you haven't read.** Hop looked like 12 to 15 of 18. An answer listing every band
  contains the right one.
- **Crediting the wrong part.** The query alone gained about 4 points. Test the parts apart.
- **Forgetting the cost.** Count model calls and tokens, not just the score.
- **Reading "I assume" as a detail.** It's the model telling you it needed another search.
- **Saying agents beat everything.** You've only shown the setups you measured.

## Recap

- `search_tool` turns any index into a tool, and `AGENT_SYSTEM` tells the agent to use it. The model now
  writes the query and decides when to stop.
- Agents scored 112 to 119, against 97 to 105 for one-shot setups. With a stricter hop check, it was 107
  to 114 against 96 to 102. It's the clearest gain in Part 4.
- It cost about twice the model calls, and more tokens.
- Most of the search work was one good query. `agent60` searched again in 9 runs of 252, and that
  helped when the first words missed, as on `riverside-repair`.
- No agent run saw both files on the 4 questions that need them. Multi-hop isn't solved here.
- Prompts didn't change that. `Split`, which puts the second search in your code, found both files in
  half of those runs, and its passes came from having the facts.
- Failures to look for: a made-up band after a good search, a list of every option, a search that
  runs out of steps, and a rule invented from finding nothing.

## Part 4 in one page

You started with a search that couldn't find "footwear" in a handbook that says "shoes".

- **Chapter 19:** embeddings let you search by meaning, and cosine compares them.
- **Chapter 20:** pasting works until the text is silently cut, so you chunked, searched and asked once.
  And if your documents fit, you may not need RAG.
- **Chapter 21:** titles gave each chunk back the words that say what it's about. Close scores can't be
  ranked.
- **Chapter 22:** keyword search and fusion found what vectors missed, and reranking didn't earn its cost.
- **Chapter 23:** the agent chose its own query, for the biggest gain, at twice the calls. It still didn't
  chain two facts, until your code made the second search.

The thread through all four is the habit, not any one technique: feel the problem, build the simplest
thing, measure it, and then read what failed.

## Where this comes from

Letting a model mix reasoning with actions such as searching comes from the 2022 paper
[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629).

**Next:** chapter 24, context management.
