# Chapter 16: Tracing and hooks

**Time:** about 2 hours. **You'll learn:** how to see inside a run, and step in, without touching
the loop.

## Where we are

In chapter 15, you wrapped the loop in an `Agent`. It works, and you can reuse it. But when you call
`agent.run()`, you only get the end of the story. This chapter adds a way to watch every step, stop
some of them, and keep a record.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. You'll work in `chapters/16-tracing-and-hooks/code`. Every script here is short, and each
one is shown before you run it, except `five_runs.py`, which is a provided measuring tool.

## 1. A run you can't see into

So far, we've asked for a total. Open [code/blind.py](code/blind.py). It asks something new:

```python
QUESTION = "Which day had the most coffee revenue?"

agent = Agent(load_model(), toolbox, options={"temperature": 0})
result = agent.run(QUESTION)
print("Answer:", result.answer)
print("Steps:", result.steps)
```

**Predict:** there are three files to read. How many steps will it take?

```bash
python3 blind.py
```

This is real output from `qwen2.5:7b`:

```text
Answer: The total coffee revenue for each day is as follows:

- **Monday:** 120
- **Tuesday:** 150
- **Wednesday:** 110

The total revenue for coffee across all days is 380 units. 

From the data, it is clear that **Tuesday** had the highest coffee revenue with 150 units sold.

Therefore, the day with the most coffee revenue is **Tuesday**.
Steps: 7
```

Tuesday is right. But why seven steps? Listing the folder, reading three files and answering makes
five. We ran it five times, and it took seven steps every time.

You can't tell why from here. You have two options so far, and neither is good:

- **Add `print` lines inside the loop.** Then the framework prints for everyone, whether they want
  it or not, and you're editing the loop each time you have a new question.
- **Use `stream()` from chapter 15.** That shows the events, but every script needs its own `for`
  loop, and an event can only tell you something happened. It can't stop it.

## 2. Hooks

A **hook** is an object the agent calls at set moments during a run. Open
[code/whitebox/hooks.py](code/whitebox/hooks.py):

```python
class Hook:
    """Override the moments you care about. The rest do nothing."""

    def before_model(self, messages):
        pass

    def after_model(self, reply):
        pass

    def before_tool(self, call):
        """Return text to block this call. The model sees that text as the result."""
        return None

    def after_tool(self, call, output):
        pass

    def on_finish(self, result):
        pass
```

This is the base class idea from chapter 03 again, with one difference. `Model.chat` raises
`NotImplementedError`, because every model must provide it. A `Hook`'s methods do nothing, because
a hook only overrides the moments it cares about.

`Printer` cares about two:

```python
class Printer(Hook):
    """Show each tool call as it happens."""

    def before_tool(self, call):
        print(f"[tool] {call.name}({call.arguments})")

    def after_tool(self, call, output):
        print(f"    -> {output!r}")
```

The `Agent` has a new `hooks` setting, which is a list. Open [code/watched.py](code/watched.py). It's
`blind.py`, with one change:

```python
agent = Agent(load_model(), toolbox, options={"temperature": 0}, hooks=[Printer()])
```

```bash
python3 watched.py
```

```text
[tool] read_file({'path': 'sales/coffee_sales.txt'})
    -> "Error: [Errno 2] No such file or directory: '.../code/workspace/sales/coffee_sales.txt'"
[tool] list_files({'folder': 'sales'})
    -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[tool] read_file({'path': 'sales/monday.txt'})
    -> 'Coffee: 120\nTea: 80\n'
[tool] read_file({'path': 'sales/tuesday.txt'})
    -> 'Coffee: 150\nTea: 95\n'
[tool] read_file({'path': 'sales/wednesday.txt'})
    -> 'Coffee: 110\nTea: 70\n'
[tool] add_numbers({'numbers': [120, 150, 110]})
    -> '380'
```

The answer that followed is the same as before, so we've left it out. We've also shortened the
start of the file path to `.../code/`, because it showed our own folders. Yours will show your path.

Now the seven steps make sense. The model **guessed a file name** that doesn't exist, read the error,
and recovered by listing the folder. Then, after reading the files, it added the three numbers, which
nobody asked for. The answer was right, and the path to it was not what you'd have assumed.

## 3. How the agent calls hooks

Open [code/whitebox/agent.py](code/whitebox/agent.py). The loop now announces each moment:

```python
self.notify("before_model", messages)
```

`notify` is the only new machinery:

```python
def notify(self, moment, *args):
    """Call one moment on every hook, and return the first thing a hook says."""
    answers = [getattr(hook, moment)(*args) for hook in self.hooks]
    return next((answer for answer in answers if answer is not None), None)
```

Two pieces of Python here are new:

- **`getattr(hook, moment)`** looks up an attribute by a name held in a string. If `moment` is
  `"before_tool"`, it gives you `hook.before_tool`, and `(*args)` then calls it.
- **`next(..., None)`** gets the first value from a generator, as in chapter 04. The brackets hold a
  generator written on one line, in the same style as a list comprehension. The second argument is
  what `next` returns if there's nothing to give, so here it never raises an error.

Every hook runs at every moment, even if an earlier hook has already answered. So a `Tracer` still
sees a call that another hook blocks.

## 4. A hook can change a run

So far, hooks only watch. The answer `notify` returns is what lets them act:

```python
def run_tool(self, call):
    """Run one tool call, unless a hook blocks it."""
    output = self.notify("before_tool", call) or self.toolbox.run(call)
    self.notify("after_tool", call, output)
    return output
```

`a or b` gives you `a` if it has a value, and only works out `b` if it doesn't. So if a hook returns
text from `before_tool`, the tool **never runs**, and that text becomes the result the model reads.
It's the same idea as chapter 10: errors go back to the model as text, and it can decide what to do.

`Approval` uses this to ask a person first:

```python
class Approval(Hook):
    """Ask a person before running certain tools."""

    def __init__(self, names, ask=input):
        self.names = names
        self.ask = ask

    def before_tool(self, call):
        if call.name not in self.names:
            return None
        if self.ask(f"Allow {call.name}({call.arguments})? (y/n) ") == "y":
            return None
        return f"Error: a person refused the call to {call.name}"
```

`ask=input` is the fake trick from chapter 05. A function is a value, so the tests can pass a
different `ask` that doesn't wait for a keyboard.

Open [code/approve.py](code/approve.py). It adds a `save_note` tool that really writes a file, and
asks the agent to use it:

```python
QUESTION = "Read sales/monday.txt, then save a note with Monday's coffee revenue."
```

```python
hooks = [Printer(), Approval(["save_note"])]
agent = Agent(load_model(), toolbox, options={"temperature": 0}, hooks=hooks)
print("Answer:", agent.run(QUESTION).answer)
print("Note saved:", NOTE.exists())
```

**Predict:** Monday's coffee revenue is 120. What number will the model try to save? Run it, read the
request carefully, and type `n`:

```bash
python3 approve.py
```

```text
[tool] read_file({'path': 'sales/monday.txt'})
    -> 'Coffee: 120\nTea: 80\n'
[tool] save_note({'text': "Monday's coffee revenue is $543.21"})
Allow save_note({'text': "Monday's coffee revenue is $543.21"})? (y/n) n
    -> 'Error: a person refused the call to save_note'
Answer: The content of the file `sales/monday.txt` indicates that on Monday, 120 cups of coffee and 80 cups of tea were sold. However, there was an issue saving the note about Monday's coffee revenue. Let's focus on the sales information for now. If you need any further analysis or have more questions, feel free to ask!
Note saved: False
```

$543.21 is a made-up number. The model asked for both tools **in one reply**, as you saw in chapter
11, so it wrote the note before it had read the file.

We ran this ten times at temperature 0.7. In 10 of 10 runs, it asked for both tools in one reply. Only
2 of the 10 notes held the right figure. The others said things like `$450` and `$3456`, and one saved
the placeholder `[revenue]`.

- **When we refused (5 runs),** the final answer said the save hadn't worked, 5 of 5 times.
- **When we approved (5 runs),** the wrong text went through. In one run, the note said `$345` while
  the answer told us `$120`. These ten runs used a stand-in `save_note` that wrote no file.

So reading the request matters. Saying `y` without looking saves the wrong number. If you do type
`y`, you'll find the note in `workspace/note.txt`, and you can delete it.

## 5. Keep a record

`Printer`'s output is gone when the run ends. If an agent went wrong last night, you need a
**trace**: a saved record of everything a run did.

A trace needs two facts we haven't kept yet: how long things took, and how many tokens they used.
Ollama already sends token counts, so `Message` has two new fields, `tokens_in` and `tokens_out`.
`OllamaModel` fills them in from `prompt_eval_count` and `eval_count`. As in chapter 13, those Ollama
names stop at the edge, and the rest of the framework only sees `tokens_in` and `tokens_out`.
`{**data["message"], **self.token_counts(data)}` in `models.py` is `**` from chapter 04 again. Here,
it builds a new dictionary from two others.

`Tracer` is a hook like the others. These are the parts that matter:

```python
def write(self, kind, **data):
    with open(self.path, "a") as file:
        file.write(json.dumps({"kind": kind, **data}) + "\n")

def before_model(self, messages):
    self.started["model"] = self.clock()

def after_model(self, reply):
    seconds = round(self.clock() - self.started["model"], 2)
    self.write("model", seconds=seconds, reply=asdict(reply))
```

- The file has **one JSON object per line**, which is called JSON Lines. Each line is written as it
  happens, so if a run crashes, the steps before the crash are still in the file.
- `self.clock` is `time.monotonic` by default, a stopwatch that gives seconds. It's a parameter so a
  test can pass a fake clock.
- `asdict` comes with dataclasses, and turns a `Message` into a plain dictionary that JSON can store.
- `open(path, "w").close()` in `__init__` empties the file, so each `Tracer` starts clean.

`show_trace` reads the file back for a person. The `:6.2f` in its f-strings means "6 characters wide,
with 2 decimal places", which keeps the columns lined up.

Open [code/demo.py](code/demo.py). It traces our coffee question from chapter 12:

```python
agent = Agent(model, toolbox, options={"temperature": 0}, hooks=[Tracer("trace.jsonl")])
agent.run(QUESTION)
show_trace("trace.jsonl")
```

**Predict:** as the run goes on, will each model call read more tokens, or fewer?

```bash
python3 demo.py
```

```text
model    2.88s    272 in   20 out  -> list_files
tool     0.00s  list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
model    4.06s    320 in   24 out  -> read_file
tool     0.00s  read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
model    7.62s    374 in   22 out  -> read_file
tool     0.00s  read_file({'path': 'sales/tuesday.txt'}) -> 'Coffee: 150\nTea: 95\n'
model    6.87s    427 in   23 out  -> read_file
tool     0.00s  read_file({'path': 'sales/wednesday.txt'}) -> 'Coffee: 110\nTea: 70\n'
model    7.06s    481 in   91 out  -> add_numbers
tool     0.00s  add_numbers({'numbers': [120, 150, 110]}) -> '380'
model    4.44s    561 in   19 out  -> answer
finish  32.93s  2634 tokens, 6 steps: The total coffee revenue across all the days in the sales folder is 380.
```

Your seconds will differ. Ours came from a machine doing other work, so don't read anything into them.

Input tokens climb on every line, from 272 to 561. That's chapter 12's lesson as a number: the model
remembers nothing, so each call resends the whole conversation. Tools took almost no time, and nearly
all the seconds went to the model.

The file itself is plain JSON, so any program can read it. These are its first two lines:

```text
{"kind": "model", "seconds": 2.88, "reply": {"role": "assistant", "content": "", "tool_calls": [{"name": "list_files", "arguments": {"folder": "sales"}}], "tool_name": null, "tokens_in": 272, "tokens_out": 20}}
{"kind": "tool", "seconds": 0.0, "name": "list_files", "arguments": {"folder": "sales"}, "output": "monday.txt\ntuesday.txt\nwednesday.txt"}
```

## 6. Use a trace to fix something

Now trace the Tuesday question. [code/traced.py](code/traced.py) is `demo.py` with that question:

```bash
python3 traced.py
```

```text
model    4.94s    265 in   94 out  -> read_file
tool     0.00s  read_file({'path': 'sales/coffee_sales.txt'}) -> "Error: [Errno 2] No such file or directory: '.../code/workspace/sales/coffee_sales.txt'"
model    7.09s    431 in   60 out  -> list_files
tool     0.00s  list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
model   11.58s    501 in   24 out  -> read_file
tool     0.00s  read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
model    6.05s    555 in   23 out  -> read_file
tool     0.00s  read_file({'path': 'sales/tuesday.txt'}) -> 'Coffee: 150\nTea: 95\n'
model    6.77s    608 in   23 out  -> read_file
tool     0.00s  read_file({'path': 'sales/wednesday.txt'}) -> 'Coffee: 110\nTea: 70\n'
model    7.87s    662 in  149 out  -> add_numbers
tool     0.00s  add_numbers({'numbers': [120, 150, 110]}) -> '380'
model    8.41s    801 in   93 out  -> answer
finish  52.71s  4289 tokens, 7 steps: The total coffee revenue for each day is as follows:
```

The last line goes on with the rest of the answer, which we've cut here. This run used 4,289 tokens.
The coffee total used 2,634, and it needs the same three files.

The first line suggests a cause. The question doesn't mention the sales folder, and the system prompt
doesn't either, so the model guessed. [code/improved.py](code/improved.py) adds one sentence:

```python
BETTER = SYSTEM + " Files are in the sales folder."
```

`system=BETTER` passes it to the `Agent`. Everything else is the same as `traced.py`.

**Predict:** will it take fewer steps?

```bash
python3 improved.py
```

```text
model   11.85s    272 in   61 out  -> list_files
tool     0.00s  list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
model    3.90s    343 in   20 out  -> list_files
tool     0.00s  list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
model    6.71s    391 in   96 out  -> read_file
tool     0.00s  read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
model    5.93s    495 in   24 out  -> read_file
tool     0.00s  read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
model    6.93s    549 in   66 out  -> read_file
tool     0.00s  read_file({'path': 'sales/tuesday.txt'}) -> 'Coffee: 150\nTea: 95\n'
model   10.39s    625 in   22 out  -> read_file
tool     0.00s  read_file({'path': 'sales/tuesday.txt'}) -> 'Coffee: 150\nTea: 95\n'
model    6.12s    678 in   67 out  -> read_file
tool     0.00s  read_file({'path': 'sales/wednesday.txt'}) -> 'Coffee: 110\nTea: 70\n'
model    2.70s    754 in   23 out  -> read_file
tool     0.00s  read_file({'path': 'sales/wednesday.txt'}) -> 'Coffee: 110\nTea: 70\n'
finish  54.53s  4486 tokens, 8 steps: Stopped: no answer after 8 steps.
```

The guess is gone, but now it makes **every call twice** and runs out of steps. We ran this four times,
and the calls were the same each time. Without the trace, all you'd see is `Stopped`.

So did the fix fail? Those runs were all at temperature 0, where one bad path repeats exactly. Agents
don't always run at temperature 0, so let's test that. `five_runs.py` is a provided measuring
tool. It runs each prompt five times at temperature 0.7, and it counts with a small `Hook` of its own.
It makes a lot of model calls, so it takes a while.

**Predict:** which prompt will name Tuesday more often?

```bash
python3 five_runs.py
```

```text
Original prompt
  Run 1: 7 steps, 6 tool calls, 0 errors, 3861 tokens
  Run 2: 7 steps, 6 tool calls, 1 errors, 4119 tokens
  Run 3: 2 steps, 1 tool calls, 1 errors, 858 tokens
  Run 4: 2 steps, 1 tool calls, 1 errors, 807 tokens
  Run 5: 2 steps, 1 tool calls, 1 errors, 795 tokens
  Named Tuesday: 2/5
Better prompt
  Run 1: 7 steps, 6 tool calls, 0 errors, 3508 tokens
  Run 2: 6 steps, 5 tool calls, 0 errors, 3115 tokens
  Run 3: 5 steps, 4 tool calls, 0 errors, 2204 tokens
  Run 4: 6 steps, 6 tool calls, 0 errors, 2889 tokens
  Run 5: 6 steps, 5 tool calls, 0 errors, 2819 tokens
  Named Tuesday: 5/5
```

We ran this batch three times:

| Prompt | Batch 1 | Batch 2 | Batch 3 | Total |
|---|---|---|---|---|
| Original | 2/5 | 2/5 | 1/5 | 5/15 |
| Better | 5/5 | 5/5 | 5/5 | 15/15 |

That changes the story twice. The original prompt, which looked fine at temperature 0, often failed at
0.7. In runs 3 to 5 above, its one tool call failed, and it stopped after 2 steps. And the better
prompt, which got stuck at temperature 0, named Tuesday in every run here.

Here's what to take from this:

- **A trace tells you why one run went the way it did.** That's how we found the guessed file.
- **A trace can't tell you how often.** One run misled us in both directions.
- **We don't know why the model repeats itself at temperature 0.** The trace shows what it did, not
  what caused it.

## What each tool is for

| You want to | Use |
|---|---|
| Watch a run in the terminal | `Printer` |
| Show a person each piece of text as it arrives | `stream()` from chapter 15 |
| Stop a tool from running | A hook that returns text from `before_tool` |
| Look at a run after it ended | `Tracer`, then `show_trace` |

## Reading errors

We caused each of these on purpose:

| What happened | What you see | The fix |
|---|---|---|
| You wrote `hooks=Printer()` | `TypeError: 'Printer' object is not iterable` | `hooks` is a list: `hooks=[Printer()]` |
| A moment has the wrong parameters | `TypeError: Bad.after_model() takes 1 positional argument but 2 were given` | Copy the parameters from `Hook` |
| You misspelled a moment, such as `after_modle` | Nothing. The run works, and your method is never called | Check the spelling against `Hook` |
| You read a trace that wasn't written | `FileNotFoundError: [Errno 2] No such file or directory: 'nope.jsonl'` | Check the path, and which folder you're in |

## Exercises

In this chapter's folder, open [exercises.py](exercises.py). You'll extend the framework with four new
hooks and a trace reader:

1. `ToolCounter`: count how many times each tool ran.
2. `TokenMeter`: add up the tokens a run used.
3. `Blocklist`: block the tools you name.
4. `ToolLimit`: allow a set number of tool calls in each run.
5. `summarize_trace`: read a trace file, and return its totals.

Then check your work from `chapters/16-tracing-and-hooks`. These checks use `FakeModel`, so Ollama
doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py). The small `pytest.ini` file in this folder tells
pytest to look in `code/`, which is how `from whitebox import Hook` finds the framework.

To run the framework's own tests, go into `code/` and run `python3 -m pytest tests`.

## Common mistakes

- **Returning something from `before_tool` by accident.** Any text you return blocks the tool. A
  hook that only watches should return nothing.
- **Reading only the final answer.** The Tuesday answer was right, and the run still guessed a file
  and added numbers for no reason.
- **Saying `y` without reading.** `Approval` only helps if a person checks the request.
- **Trusting one trace.** It shows one run. Our two temperature 0 stories both changed at 0.7.
- **Judging speed from one trace.** Timings depend on what else your machine is doing.

## Recap

- A hook is called at set moments, so you can add behavior without editing the loop.
- `notify` calls every hook, and gives back the first answer that isn't `None`.
- Returning text from `before_tool` blocks a tool, and the model reads that text as the result.
- `Approval` puts a person in front of a tool, and that person has to read what it's about to do.
- A trace records each step, with its timing and tokens, in a file.
- A trace shows why one run went the way it did. It can't show how often.

## Where this comes from

Ollama's API documentation lists the
[counts it returns](https://github.com/ollama/ollama/blob/main/docs/api.md), including
`prompt_eval_count` and `eval_count`.

**Next:** chapter 17, where you'll handle what goes wrong.
