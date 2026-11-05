# Chapter 18: Evals

**Time:** about 2 hours. **You'll learn:** how to measure an agent, and how much a small test can
and can't tell you.

## Where we are

In chapter 17, you wrapped the model in safety nets. Did they help? You can't tell yet.

Chapter 12 showed why. The same agent, on the same question, scored 5/5, then 4/5, then 5/5. That
was five runs marked by a script written for one question. You need something better before you
change a prompt, a model or a tool, and this chapter builds it: an eval.

An **eval** is a fixed set of questions with automatic checks, run several times, so you get a
score you can compare.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. You'll work in `chapters/18-evals/code`.

One file is new in the framework: `whitebox/evals.py`. `eval_sales.py` uses it. `same_agent.py` is
a provided measuring tool, and you don't need to change it. The other small scripts are explained
as you reach them.

To check the framework itself, run this from `code`:

```bash
python3 -m pytest tests
```

You should see `44 passed`. These tests use a fake model, so they don't need Ollama.

## 1. Mark the answers by eye

Open [code/by_eye.py](code/by_eye.py). It asks the coffee question five times at temperature 0.7,
and prints each answer:

```python
agent = Agent(load_model(), toolbox, options={"temperature": 0.7})
for run in range(1, 6):
    result = agent.run(QUESTION)
    print(f"Run {run}, {result.steps} steps: {result.answer}")
```

**Predict:** how many of the five will be right? Then run it:

```bash
python3 by_eye.py
```

This is real output from `qwen2.5:7b`:

```text
Run 1, 6 steps: The total coffee revenue across all the days in the sales folder is 380.
Run 2, 6 steps: The total coffee revenue across all the days in the sales folder is 380.
Run 3, 6 steps: The total coffee revenue across all the days in the sales folder is 380.
Run 4, 6 steps: The total coffee revenue across all the days in the sales folder is 380.
Run 5, 6 steps: The total coffee revenue across all the days in the sales folder is 380.
```

Five out of five, this time. You were the check: you read each line, and looked for 380.

Now imagine doing that for five different questions, on two versions of your agent, every time you
change something. That's 50 answers to read, some of them long. Nobody does that twice, so the
marking has to become code.

## 2. A check is a label and a test

Open [code/whitebox/evals.py](code/whitebox/evals.py). The smallest piece is a `Check`:

```python
@dataclass
class Check:
    label: str
    test: Callable


def contains(text):
    return Check(f"contains {text!r}", lambda result: text in result.answer)
```

Two things here are new:

- **`Callable`** is the type hint for "a function". `test` holds a function that takes a `Result`,
  and returns `True` or `False`.
- **`lambda`** writes a small function with no name, in one line. `lambda result: text in
  result.answer` means the same as `def test(result): return text in result.answer`.

`contains("380")` builds a check that remembers `"380"`, just as chapter 04's decorators remembered
the function they wrapped. The label is for people, so a failure can tell you what went wrong.

A check can look at more than the answer, because a `Result` holds the whole conversation:

```python
def tools_used(result):
    return [call.name for message in result.messages for call in message.tool_calls]


def used_tool(name):
    return Check(f"used {name}", lambda result: name in tools_used(result))


def finished():
    return Check("finished", lambda result: not result.stopped)
```

`excludes(text)` and `used_no_tools()` work the same way.

## 3. A case, run several times

A **case** is one question and the checks its answer must pass. Open
[code/one_case.py](code/one_case.py):

```python
case = Case(
    "coffee total",
    "What was the total coffee revenue across all the days in the sales folder?",
    [contains("380"), used_tool("add_numbers"), finished()],
)

agent = Agent(load_model(), toolbox, options={"temperature": 0.7})
report = run_eval(agent, [case], runs=5, label="first eval")
print(report.table())
print(report.rows[0].failures)
```

`run_eval` is the part that replaces you:

```python
for case in cases:
    row = Row(case.name)
    for run in range(runs):
        result = agent.run(case.question)
        failed = [check.label for check in case.checks if not check.test(result)]
        row.runs += 1
        row.steps += result.steps
        if failed:
            row.failures.append({"run": run + 1, "failed": failed, "answer": result.answer})
        else:
            row.passed += 1
    rows.append(row)
```

A run passes only if every check passes. A failed run is kept, with its answer and the labels that
failed, so you can read it later. Run it:

```bash
python3 one_case.py
```

```text
first eval
Case                  Passed  Steps
coffee total             5/5    6.0
Total                    5/5
[]
```

`Steps` is the average number of times the model was called, and `[]` means no failures to read.
You'll see a real failure soon.

## 4. A check can be wrong too

You've handed the marking to `contains`. Can you trust it? [code/weak_checks.py](code/weak_checks.py)
tries it on answers we wrote ourselves, so it needs no model:

```python
check = contains("380")
answers = ["The total is 380.", "The total is $1,380.", "The total is 3800.", "Three hundred and eighty."]
for answer in answers:
    print(f"{check.test(Result(answer, [], 1))!s:5}  {answer}")

check = excludes("120")
for answer in ["There's no Friday file, so I can't say.", "No Friday file. Monday was 120."]:
    print(f"{check.test(Result(answer, [], 1))!s:5}  {answer}")
```

**Predict:** which of these will the checks get wrong? (`!s:5` only pads the word to five letters.)

```text
True   The total is 380.
True   The total is $1,380.
True   The total is 3800.
False  Three hundred and eighty.
True   There's no Friday file, so I can't say.
False  No Friday file. Monday was 120.
```

Four mistakes in six. `contains("380")` passes two wrong totals, and fails a right one written in
words. `excludes("120")` fails an honest answer that happened to mention Monday. Your eval measures
your checks as well as your agent. You'll write a stricter number check in the exercises.

## 5. The full eval

Open [code/eval_sales.py](code/eval_sales.py). It has five cases, chosen to cover different kinds of
behavior, not just the happy path:

```python
CASES = [
    Case("coffee total", "What was the total coffee revenue across all the days in the sales folder?",
         [contains("380"), used_tool("add_numbers"), finished()]),
    Case("tea total", "What was the total tea revenue across all the days in the sales folder?",
         [contains("245"), finished()]),
    Case("one day", "What was the coffee revenue on Tuesday? The files are in the sales folder.",
         [contains("150"), used_tool("read_file"), finished()]),
    Case("missing day", "What was the coffee revenue on Friday? The files are in the sales folder.",
         [excludes("120"), excludes("150"), excludes("110"), finished()]),
    Case("no tool needed", "Say hello in one short sentence.", [used_no_tools(), finished()]),
]
```

"missing day" checks that the agent doesn't pass off another day's number as Friday's. "no tool
needed" checks that it doesn't reach for a tool it doesn't need.

The script runs the eval on two agents, each five runs per case, and compares them:

```python
before = run_eval(Agent(plain, toolbox, options=options), CASES, label="plain")
after = run_eval(
    Agent(Retry(RescueToolCalls(plain)), toolbox, options=options, hooks=[LoopGuard()]),
    CASES,
    label="reliable",
)
```

`plain` is the bare model. `reliable` has chapter 17's safety nets. `compare` puts the two reports
side by side, using `zip`, which walks through two lists together, one pair at a time. Each report is
also saved as JSON with `save`, so you can read its failures later or compare it with a future run.

**Predict:** will the safety nets raise the score? It makes well over a hundred model calls, so it
takes a while.

```bash
python3 eval_sales.py
```

```text
plain
Case                  Passed  Steps
coffee total             4/5    5.8
tea total                5/5    6.0
one day                  5/5    2.0
missing day              4/5    3.0
no tool needed           5/5    1.0
Total                  23/25

reliable
Case                  Passed  Steps
coffee total             5/5    6.0
tea total                5/5    5.8
one day                  5/5    2.0
missing day              5/5    2.8
no tool needed           5/5    1.0
Total                  25/25

Case                        plain     reliable
coffee total                  4/5          5/5  +1
tea total                     5/5          5/5
one day                       5/5          5/5
missing day                   4/5          5/5  +1
no tool needed                5/5          5/5
```

23 became 25. It's tempting to write "the safety nets worked" and move on.

## 6. Is 25 really better than 23?

Here's a test you should run before you trust any comparison: compare an agent with itself. Nothing
changes between rounds, so any movement in the score is pure chance. This is called an **A/A test**.

[code/same_agent.py](code/same_agent.py) is a provided measuring tool. It runs the same eval on the
same agent, round after round, and prints each score:

```python
for number in range(1, rounds + 1):
    report = run_eval(agent, CASES, label=kind)
    passed, runs = report.score()
    missed = [f"{row.name} {row.runs - row.passed}" for row in report.rows if row.passed < row.runs]
    print(f"{kind} round {number}: {passed}/{runs}  {', '.join(missed)}", flush=True)
```

**Predict:** the agent, the cases and the settings never change. How far will the score move? We
ran six rounds, which takes a long time. Try `3` instead of `6` if you want a shorter run:

```bash
python3 same_agent.py plain 6
```

```text
plain round 1: 24/25  coffee total 1
plain round 2: 25/25
plain round 3: 21/25  coffee total 3, tea total 1
plain round 4: 23/25  coffee total 2
plain round 5: 24/25  coffee total 1
plain round 6: 24/25  coffee total 1
```

The same agent scored anywhere from 21 to 25. So 23 and 25 are both ordinary scores for the plain
agent, with no change at all. The "improvement" in section 5 could be nothing but chance.

Look at one more clue. "missing day" scored 4/5 in section 5, but it passed all 30 runs here. That
one failure told us very little.

Now the other agent:

```bash
python3 same_agent.py reliable 6
```

```text
reliable round 1: 25/25
reliable round 2: 25/25
reliable round 3: 25/25
reliable round 4: 22/25  coffee total 3
reliable round 5: 24/25  coffee total 1
reliable round 6: 25/25
```

| Agent | Total over 6 rounds | Lowest round | Highest round |
|---|---|---|---|
| plain | 141/150 | 21/25 | 25/25 |
| reliable | 146/150 | 22/25 | 25/25 |

The ranges overlap almost completely, and even 150 runs each gives a gap of just five passes.
Reliable may be a little better, but this total doesn't prove it. Here's the rule to remember:

> A difference only means something if it's bigger than the difference between an agent and itself.

So measure that first. More runs help, but they cost time, so spend them on the comparisons that
matter.

## 7. Read the failures

The total hides the most useful thing an eval gives you. We saved all 12 reports and read every
failure. There are 13:

| What happened | plain | reliable |
|---|---|---|
| Right answer of 380, but did the sum itself, so `used add_numbers` failed | 3 | 4 |
| Stopped after 8 steps | 2 | 0 |
| Wrote a tool call as text, so the run ended there | 2 | 0 |
| Said "I'll add these numbers", then stopped without doing it | 1 | 0 |
| Gave a wrong total, 530 | 1 | 0 |
| **Total** | **9** | **4** |

Three things stand out:

- **None of reliable's failures is a wrong answer.** All 4 gave the right total. They failed a check
  that says *how* to get there. Is that a real failure? It depends on what you
  care about. A model doing mental arithmetic may be fine for three small numbers, and risky for
  three hundred. You decide, then you write the check to match.
- **The kinds of failure differ more than the scores do.** Plain failed the answer check in 6 of 150
  runs, and reliable in 0 of 150. That's a more interesting gap than 141 versus 146, though 6 is
  still a small number, and `contains` can pass a wrong total, as you saw in section 4.
- **Don't guess at the cause.** The two text tool calls looked like this:

  ```text
   Ronaldo
  {"name": "add_numbers", "arguments": {"numbers": [120, 150, 150]}}
  </tool_call>
  ```

  We passed both real replies to `RescueToolCalls`, and it rescued neither, because of the stray
  word before the JSON. So that safety net didn't prevent this failure, whatever the table seems to
  suggest. It's a real gap that only reading failures could find. The eval tells you where to look,
  and it doesn't tell you why.

To read failures yourself, open `plain.json`, which `eval_sales.py` saves. Each row has a `failures`
list holding the run, the labels that failed and the answer.

## 8. When code can't check it

Some questions don't have a number to look for. Was the answer honest? Was it polite? For these,
you can ask a model to grade the answer. This is called an **LLM judge**:

```python
def judged(model, rubric):
    """Ask a model to grade the answer, for checks that plain code can't make."""

    def test(result):
        prompt = f"Rubric: {rubric}\n\nAnswer: {result.answer}\n\nReply with only PASS or FAIL."
        reply = model.chat([Message("user", prompt)], temperature=0)
        return reply.content.strip().upper().startswith("PASS")

    return Check(f"judged: {rubric}", test)
```

A judge is a model, so it can be wrong. Test it before you trust it. Open
[code/judge_test.py](code/judge_test.py). It holds six answers to the Friday question that we marked
by hand, then grades each one with the judge, and with `excludes("120")`:

```python
RUBRIC = "The answer says the Friday figure isn't available, and gives no number for Friday."
```

**Predict:** which will get more right, the judge or the code? Then run it:

```bash
python3 judge_test.py
```

```text
Right  Judge  Code   Answer
True   True   True   There is no file for Friday, so I can't tell you the coffee revenue.
True   True   True   I couldn't find a Friday file in the sales folder.
True   True   False  There's no Friday file. Monday was 120, Tuesday 150 and Wednesday 110.
False  False  True   The coffee revenue on Friday was 130.
False  True   True   There's no Friday file, but it was probably about 127.
False  False  True   Friday's coffee revenue was 0.
```

The judge matched our marks on 5 of 6, and the code on 2 of 6. That's not a fair fight, because
`excludes("120")` only looks for one number, but no simple code check can read for honesty. The
judge understood that listing other days is fine. But it passed "probably about 127", which breaks the rubric. It gave the same
six grades in 5 of 5 runs, so that mistake is steady, not bad luck.

Here the judge is the same small model as the agent, so it shares the agent's weaknesses. Prefer a
code check when one can do the job. When you do use a judge, mark some answers by hand first, and
measure it the way you just did.

## Reading errors

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `whitebox.models.ModelError: Couldn't reach Ollama` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| You passed a function, not a `Check` | `AttributeError: 'function' object has no attribute 'test'` | Wrap it: `Check("label", function)` |
| You printed a table after `runs=0` | `ZeroDivisionError: division by zero` | Use `runs=1` or more |

## Exercises

From `chapters/18-evals`, open [exercises.py](exercises.py) and complete the five TODOs. Each one
extends the eval system:

1. `equals_number`: a stricter check, which fixes the mistakes from section 4.
2. `steps_at_most`: fail a run that took too many steps.
3. `tool_count`: check how many times a tool was used.
4. `failed_checks`: count which checks fail most often.
5. `clear_changes`: list only the cases that moved by more than a margin.

The `sys.path` line at the top of `exercises.py` is provided. It lets the file find the `whitebox`
package inside `code/`. `numbers_in` is provided too. It uses the `re` module to find numbers in
text, and you don't need to know how.

Then check your work from `chapters/18-evals`. These checks use a fake model, so Ollama doesn't need
to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Part 3 checkpoint

You've finished Part 3. Before moving on, complete the
[Part 3 checkpoint](../../checkpoints/part-3/README.md), a trip expenses agent rebuilt on your
framework, and measured, using everything from chapters 13 to 18.

## Common mistakes

- **Comparing two single scores.** Run an agent against itself first, to see how far it moves alone.
- **Only reading the total.** The failures tell you what to fix.
- **Trusting a check you haven't tested.** Try each one on answers you've marked by hand.
- **Testing only the happy path.** Include questions the agent should refuse, and ones that need no tool.
- **Testing at temperature 0 only.** You'd get a steady score that hides how the agent behaves at
  the temperature you actually use.
- **Tuning until the eval passes.** If you keep changing the agent to fit five cases, you learn
  about those five cases, and nothing else.

## Recap

- An eval is fixed cases, automatic checks and repeated runs.
- A check is a label and a test. A case is a question and its checks.
- Your checks can be wrong, so test them too.
- Compare an agent with itself first. A difference smaller than that means nothing.
- Read the failures. They tell you more than the score.
- An LLM judge can check what code can't, and it can be wrong as well.

## Where this comes from

Using a strong model as a grader was studied in the 2023 paper
[Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685), which also describes the biases a judge
can have.

**Next:** chapter 19, where you'll start Part 4 with embeddings and vector search.
