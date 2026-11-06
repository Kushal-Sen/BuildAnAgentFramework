# Chapter 27: Durable execution

**Time:** about 2 hours. The long runs are optional. **You'll build:** a refund job that can be killed at the
worst moment and started again, without paying anyone twice and without stopping early.

## Where we are

Chapter 26 ended on a plan that ran seven model calls for one question. Longer runs have a new way to fail. The
machine restarts, someone stops the program, or the process runs out of memory. It stops mid-step, with no error
your code can catch and no chance to tidy up.

For a search, that's annoying. You ask again. But some tools change the world, and then "run it again" is the
dangerous option. This chapter gives an agent a job that pays money, and kills it right after a payment.

By the end you'll have `durable.py`: `Checkpoint`, `load_messages`, `once` and `until_done`. You'll add them one
at a time, because each one fails in a way that shows why you need the next.

This is the last chapter of Part 5, and the thread gets its last word: **let the model make the judgement call,
and keep the facts, the order and the truth in code.** Here, the truth is what the bank says.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in chapter 05. You'll
work in `chapters/27-durable-execution/code`.

One file is new in the framework: `whitebox/durable.py`. You'll read all of it. `agent.py` doesn't change. These
things are provided, and you don't need to change them:

- `refunds.py` holds the job's shared parts: six orders, the pretend bank, the two tools and the agent. Section 1
  reads the parts that matter. The orders and the bank are made up for this chapter, and no real money moves.
- `crash_test.py`, `one_reply.py`, `job_replies.py`, `look_at_save.py` and `read_crashes.py` are measuring scripts.
  Each section says what the script does.
- `results/` holds our saved runs. `read_crashes.py` uses your own file if you've made one, and ours if not. So
  **you can follow the whole chapter without the long runs.** Files your runs make stay out of git, because this
  chapter's `.gitignore` covers them.

To check the framework itself, run this from `code`:

```bash
python3 -m pytest tests
```

You should see `87 passed`. These tests use a fake model, so they don't need Ollama.

## 1. A job that pays people

Quillon Coffee has six refunds to pay. The agent gets two tools. Here's the one that matters, from
[code/refunds.py](code/refunds.py):

```python
@tool
def issue_refund(order: Annotated[str, "The order number, such as QC-101"]) -> str:
    """Refund one order. This pays real money."""
    if order not in ORDERS:
        return f"Error: no order called {order}"
    bank.pay(order)
    made["payments"] += 1
    if made["payments"] == crash_after:
        os.kill(os.getpid(), KILL)  # The worst moment: the money has gone, and nothing has been saved.
    return f"Refunded {order}."
```

Ignore the two lines with `crash_after` for now. `bank.pay` is the pretend bank:

```python
def pay(self, order):
    with self.path.open("a") as file:
        file.write(json.dumps({"order": order, "amount": ORDERS[order]}) + "\n")
```

The `"a"` means append, so each payment adds a line and nothing is ever rewritten. A file with one JSON object on each
line is often named `.jsonl`. Think of this file as something outside your program: once a line is in it, the money
has gone, and you can't take it back by deleting a variable.

[code/job_restart.py](code/job_restart.py) is the whole job:

```python
crash_after, folder = job_settings()
agent = job_agent(refund_tools(Bank(folder), crash_after))
result = agent.run(TASK)
print(one_line(result.answer))
```

`job_settings` reads two optional values from the command line, and `one_line` shortens an answer to one line.
`job_agent` builds the agent you know, wrapped in chapter 17's `Retry` and `RescueToolCalls`. The system prompt says to
call `list_refunds`, then `issue_refund` for each order, one at a time, and to reply `DONE`.

```bash
python3 job_restart.py
cat bank.jsonl
```

```text
DONE
{"order": "QC-101", "amount": 4.5}
{"order": "QC-102", "amount": 12.0}
{"order": "QC-103", "amount": 3.2}
{"order": "QC-104", "amount": 7.75}
{"order": "QC-105", "amount": 18.4}
{"order": "QC-106", "amount": 5.1}
```

Six orders, six lines. Delete `bank.jsonl` now, because the bank keeps every line until you do.

## 2. Kill it

Now those two lines. They're how we crash on purpose:

```python
os.kill(os.getpid(), KILL)
```

This is new Python:

- `os.getpid()` gives this process's own number. Every running program has one.
- `os.kill(number, signal)` sends a signal to a process. A signal is a message from the operating system.
- `KILL` is `signal.SIGKILL`, from Python's `signal` module. A process can't catch this one. No `except` runs, no
  `finally` runs, and no hook fires. It's the closest thing to someone pulling the plug.
- Windows has no `SIGKILL`, so `refunds.py` falls back to `SIGTERM` there. We haven't tested on Windows.

The kill comes right after a payment, on purpose. The money has gone, and nothing in your program knows yet. A crash
can land anywhere, so a test should use the worst place.

To kill a process and carry on, you need a second process. That's [code/crash_once.py](code/crash_once.py):

```python
def attempt(job, crash_after, folder):
    """Run the job as a separate process. Return its exit code and the last of what it printed."""
    command = [sys.executable, job, str(crash_after), str(folder)]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=LIMIT)
    except subprocess.TimeoutExpired:
        return None, f"Stopped after {LIMIT} seconds"
    return done.returncode, done.stdout.strip()[-200:]
```

- `subprocess.run` starts another program and waits for it. `command` is the list you'd type in a terminal, split
  into pieces.
- `sys.executable` is the path of the Python running this script, so the job uses your `.venv`.
- `capture_output=True` keeps what the job prints, and `text=True` gives it to you as a string.
- `timeout=LIMIT` is the line to copy. After 180 seconds, Python stops the job and raises `TimeoutExpired`. Every
  process our scripts start has a limit, and section 10 shows why.
- `returncode` is the exit code: 0 means the job finished. A negative number means a signal killed it, so `-9` is
  signal 9, `SIGKILL`.

The script deletes a folder called `run`, so the bank starts empty. Then it runs the job with a crash, runs it again
with no crash, and reads the bank. **Predict:** the job dies after paying two orders. What will the second run do?

```bash
python3 crash_once.py job_restart.py 2
```

```text
First run: exit code -9
Bank: QC-101 QC-102
Second run: exit code 0. It said: DONE
Bank: QC-101 QC-102 QC-101 QC-102 QC-103 QC-104 QC-105 QC-106
Paid twice: QC-101 QC-102
Not paid: nobody
```

Read the second run's line. Exit code 0, and it said `DONE`. Nothing failed, and two customers got their money twice.

The new process knew nothing, because `messages` died with the old one. It's chapter 25's problem again: a list that
disappears with the run. So it did what it was told, from the top.

## 3. Save before each model call

The fix looks obvious. Write the conversation to disk as you go, and read it back on a restart. Here's the
saving part of [code/whitebox/durable.py](code/whitebox/durable.py):

```python
class Checkpoint(Hook):
    """Save the conversation before each model call and after each tool, so a new process can pick it up."""

    def __init__(self, path):
        self.path = Path(path)
        self.messages = []

    def save(self, messages):
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps([asdict(message) for message in messages]))
        os.replace(temporary, self.path)  # All or nothing: a crash can't leave half a file.

    def before_model(self, messages):
        self.messages = messages
        self.save(messages)
```

It's a `Hook`, like `Memory`, and `before_model` runs before every model call. `asdict` turns a `Message` dataclass
into a dictionary, which is what `json.dumps` can write. You used it in chapter 16's `Tracer`.

`save` writes the way `Memory` does. `os.replace(a, b)` renames `a` to `b`, replacing `b`, in one step. So a process that
dies mid-write leaves a broken `.tmp` file, and the last good save is still there. That matters more here than it did
for notes, because this file is written while you expect crashes.

Reading it back is the other half:

```python
def load_messages(path):
    """Read a checkpoint back, or return None if there's nothing to resume."""
    path = Path(path)
    if not path.exists():
        return None
    messages = []
    for data in json.loads(path.read_text()):
        data["tool_calls"] = [ToolCall(**call) for call in data["tool_calls"]]
        messages.append(Message(**data))
    return messages
```

JSON gives back dictionaries, so this rebuilds real `Message` and `ToolCall` objects. `Message(**data)` passes each key
as a named argument.

The finished `Checkpoint` also saves after each tool. We want to test the simple version first, so
[code/job_saved.py](code/job_saved.py) switches that off:

```python
class BeforeEachCall(Checkpoint):
    """Our first try. It saves before each model call, and does nothing after a tool."""

    def after_tool(self, call, output):
        pass


crash_after, folder = job_settings()
state = folder / "state.json"
agent = job_agent(refund_tools(Bank(folder), crash_after), [BeforeEachCall(state)])
saved = load_messages(state)
result = agent.run(AGAIN, saved) if saved else agent.run(TASK)
print(one_line(result.answer))
```

The last lines are the whole of resuming. If there's a save, pass it as `history`, with a new message: `AGAIN` says
"You were interrupted. Carry on with the orders that aren't done yet, then reply DONE." **Predict:** it saves before
every model call. How many people get paid twice now?

```bash
python3 crash_once.py job_saved.py 2
```

```text
First run: exit code -9
Bank: QC-101 QC-102
Second run: exit code 0. It said: DONE
Bank: QC-101 QC-102 QC-101 QC-102 QC-103 QC-104 QC-105 QC-106
Paid twice: QC-101 QC-102
Not paid: nobody
```

That's exactly what starting again did. So what's in the save?

## 4. One reply, six payments

[code/look_at_save.py](code/look_at_save.py) kills a job, and prints the checkpoint before anything restarts it:

```bash
python3 look_at_save.py job_saved.py 2
```

Lines are cut at 60 characters by the script:

```text
Exit code -9. Bank: QC-101 QC-102
The save holds:
  system: You process refunds. Call list_refunds, then call issue_refu
  user: Process today's refunds.
  assistant: asked for 1 list_refunds
  tool: QC-101: 4.50 QC-102: 12.00 QC-103: 3.20 QC-104: 7.75 QC-105:
```

Two payments have gone, and the save doesn't mention either. It ends with the list of orders. So the model is back at
the moment it first saw the list, and it pays from the top.

Why was there no save between the payments? Because there was no model call between them. The system prompt says "one
at a time", but look at what the model did. [code/one_reply.py](code/one_reply.py) runs the job with no crash, and
[code/job_replies.py](code/job_replies.py) adds a small hook that notes what each reply asked for:

```python
def after_model(self, reply):
    counts = Counter(call.name for call in reply.tool_calls)
    asked = [f"{count} {name}" for name, count in counts.items()]
    self.seen.append(" + ".join(asked) or one_line(reply.content, 20))
```

`Counter`, from `collections`, counts how often each thing appears. The script runs each job through `attempt`, so
each one has a time limit.

```bash
python3 one_reply.py
```

```text
run 1: 1 list_refunds | 77 issue_refund | Refunded QC-106. DON | bank: 77 payments, 0 unpaid
run 2: 1 list_refunds | 6 issue_refund | DONE | bank: 6 payments, 0 unpaid
run 3: 1 list_refunds | 7 issue_refund | DONE | bank: 7 payments, 0 unpaid
run 4: 1 list_refunds | 6 issue_refund | DONE | bank: 6 payments, 0 unpaid
run 5: 1 list_refunds | 6 issue_refund | DONE | bank: 6 payments, 0 unpaid
```

Each `|` separates one model reply. **All the payments arrive in one reply.** The agent loop from chapter 12 runs a
reply's tool calls one after another, with no model call in between. So a save before each model call sits before the
whole batch.

Then look at runs 1 and 3. There was no crash, and the bank paid 77 times, then 7. That was the first time we ran this
script, and we didn't plan it. So we ran it 30 more times, and the file is in
[code/results/one_reply_30_runs.txt](code/results/one_reply_30_runs.txt). Over all 35 runs:

| What happened, with no crash | Runs |
|---|---|
| One reply with all the payments, six payments in the bank | 30 |
| One reply with seven calls, and the tool refused the extra one, so six payments | 2 |
| One reply with repeats, so the bank paid too many | 2 |
| Stopped at the 180-second limit, with nothing to read | 1 |

So every run that finished put its payments in one reply, on this model, with this prompt. And a crash isn't the only way
to pay someone twice. Hold on to that. Section 6 fixes both, and section 10 comes back to run 1.

## 5. Save after each tool too

If the batch is the gap, save inside the batch. This is the rest of `Checkpoint`:

```python
    def after_tool(self, call, output):
        self.save(self.messages + [Message("tool", output, tool_name=call.name)])

    def on_finish(self, result):
        if not result.stopped:
            self.path.unlink(missing_ok=True)  # A finished run has nothing to resume. A stopped one does.
```

`self.messages` is the same list the agent is using, so it already holds the reply and the earlier results. The agent
adds this result after the hook runs, which is why `after_tool` adds it here. `on_finish` deletes the file, so the next
job doesn't resume a finished one. A run stopped by `max_steps` hasn't finished, so it keeps its save.

[code/job_saved_tools.py](code/job_saved_tools.py) is `job_saved.py` with the plain `Checkpoint`. **Predict:** the job dies
after two payments, and now it saves after each one. Will anyone be paid twice?

```bash
python3 crash_once.py job_saved_tools.py 2
```

```text
First run: exit code -9
Bank: QC-101 QC-102
Second run: exit code 0. It said: DONE
Bank: QC-101 QC-102 QC-102 QC-103 QC-104 QC-105 QC-106
Paid twice: QC-102
Not paid: nobody
```

Better, and still wrong. QC-101 was remembered, and QC-102 was paid twice. The save shows why:

```bash
python3 look_at_save.py job_saved_tools.py 2
```

```text
Exit code -9. Bank: QC-101 QC-102
The save holds:
  system: You process refunds. Call list_refunds, then call issue_refu
  user: Process today's refunds.
  assistant: asked for 1 list_refunds
  tool: QC-101: 4.50 QC-102: 12.00 QC-103: 3.20 QC-104: 7.75 QC-105:
  assistant: asked for 6 issue_refund
  tool: Refunded QC-101.
```

The bank has two payments. The save has one result. The second payment landed, and the process died before
`after_tool` ran. The gap is small, but it's there.

Can you close it by saving first? No. Save "paid QC-102" before paying, and a crash in between says it's paid when it
isn't, so a customer gets nothing. **The bank and your file are two separate systems, and you can't write to both in
one step.** Whichever goes first, a crash can land between them.

So saving more often can't finish this job. One more thing about that save: it holds a reply that asked for six calls,
and only one result. A resume doesn't finish that batch. It hands the messages back, and the model decides what to do.
You're relying on it to read that correctly.

## 6. Ask the real system

Stop trying to make your notes perfect. Before paying, ask the one place that can't be out of date:

```python
def once(tool, done):
    """Make a tool safe to repeat. done(**arguments) asks the real system whether this already happened."""

    def guarded(**arguments):
        if done(**arguments):
            return f"Already done, so nothing changed: {arguments}"
        return tool(**arguments)

    return Tool(tool.name, tool.description, tool.parameters, guarded)
```

`once` wraps a tool and gives back a tool with the same name and description, so the model can't tell. `**arguments`
collects whatever named arguments the tool was called with, and passes them on. It's the same shape as `with_timeout` in
chapter 17: a function inside a function, which remembers `tool` and `done`.

`done` is yours to write, because only you know how to ask your system. Here it's already there:

```python
def paid(self, order):
    return order in self.payments()
```

[code/job_once.py](code/job_once.py) adds one line of wiring:

```python
list_refunds, issue_refund = refund_tools(bank, crash_after)
agent = job_agent([list_refunds, once(issue_refund, bank.paid)], [Checkpoint(state)])
```

`bank.paid` has no brackets, so the function itself goes in, and `once` calls it later. A tool that gives the same
result however many times you call it is called *idempotent*, and this wrapper makes `issue_refund` act like one.

```bash
python3 crash_once.py job_once.py 2
```

```text
First run: exit code -9
Bank: QC-101 QC-102
Second run: exit code 0. It said: DONE
Bank: QC-101 QC-102 QC-103 QC-104 QC-105 QC-106
Paid twice: nobody
Not paid: nobody
```

Six orders, six lines. The model can ask to pay QC-102 again, and it doesn't matter, because the bank's answer decides.
That also covers section 4's run with no crash: it's the same check, whoever is repeating.

Notice what the check doesn't need. It doesn't trust the save, and it doesn't trust the model. The checkpoint now only
saves work, and the bank keeps the truth.

## 7. The job that said DONE

Try a crash later in the batch. **Predict:** the job dies after five payments of six, with `once` in place. What's left to
go wrong?

```bash
python3 crash_once.py job_once.py 5
```

The job cuts answers at 100 characters:

```text
First run: exit code -9
Bank: QC-101 QC-102 QC-103 QC-104 QC-105
Second run: exit code 0. It said: <tool_response> Refunded QC-105. </tool_response> <tool_response> Refunded QC-106. </tool_response>
Bank: QC-101 QC-102 QC-103 QC-104 QC-105
Paid twice: nobody
Not paid: QC-106
```

Nobody was paid twice, and **QC-106 got nothing**. Read what the model said. `<tool_response>` isn't a tool call. It's the
model *typing out* what a tool's result would look like, as plain text. It wrote "Refunded QC-106." No tool ran, no
money moved, and the bank shows five lines.

To the agent loop, a reply with text and no tool calls is a final answer. So the run ended with exit code 0, and the
checkpoint was deleted. `RescueToolCalls` from chapter 17 didn't help, because this isn't a tool call in the wrong place.
It's a report of one that never happened.

In section 9's crash test, this happened after four of the crashes at payment 5 with `once`, and four with the
plain `Checkpoint`. That's 8 of 9 crashes at that point. It didn't happen in any of the 29 crashes at payments 2, 3 and
4 with those two setups. We think one missing order on a nearly finished list is easy for this model to pass over, but
we didn't test that. It's what this 7B model did on this job. A bigger one may not do it. What holds for any model is
narrower: **the job's own report of being finished isn't evidence.**

## 8. Let the bank decide

You already have something that knows what's unpaid. So ask it, and keep asking until it says nothing's left:

```python
def until_done(agent, left, ask, history=None, tries=3):
    """Run until the real system says nothing is left, because a model can claim it finished when it didn't."""
    result = None
    for _ in range(tries):
        items = left()
        if not items:
            break
        result = agent.run(ask(items), history)
        history = result.messages
    return result
```

- `left` is a function that asks the real system what's still to do.
- `ask` turns that list into the message for the model, so the model is told what the bank shows, not what it remembers.
- `history` carries the conversation from one round to the next. `Checkpoint` deletes its file when a run ends with an answer,
  even a run that only claimed to be done, but `result.messages` still holds everything.
- If nothing's left when it starts, the model is never called, and it returns `None`.
- `tries` stops it going round forever. **If the tries run out, it just returns.** It doesn't tell you. So check `left()`
  yourself afterwards. Exercise 4 does.

[code/job_until_done.py](code/job_until_done.py) is the finished job:

```python
def still_to_do(orders):
    return f"The bank shows these orders still need issue_refund: {', '.join(orders)}. Call it for each, then reply DONE."


crash_after, folder = job_settings()
state = folder / "state.json"
bank = Bank(folder)
list_refunds, issue_refund = refund_tools(bank, crash_after)
agent = job_agent([list_refunds, once(issue_refund, bank.paid)], [Checkpoint(state)])
result = until_done(agent, bank.unpaid, still_to_do, load_messages(state))
print(one_line(result.answer) if result else "Nothing to do.")
print("Still unpaid:", bank.unpaid() or "nothing")
```

`bank.unpaid` goes in with no brackets, as `bank.paid` did. The script's last line asks the bank, not the model.

```bash
python3 crash_once.py job_until_done.py 5
```

```text
First run: exit code -9
Bank: QC-101 QC-102 QC-103 QC-104 QC-105
Second run: exit code 0. It said: DONE
Still unpaid: nothing
Bank: QC-101 QC-102 QC-103 QC-104 QC-105 QC-106
Paid twice: nobody
Not paid: nobody
```

`until_done` needs a real system to ask. A bank can say what's paid. "Write a good report" has no outside record, so
there's nothing for `left` to read, and this doesn't help with a job like that.

## 9. The whole table

One crash each proves little. [code/crash_test.py](code/crash_test.py) does the same thing 20 times for a job: five crashes
after payment 2, then 3, 4 and 5. Each gets a new empty bank, from `tempfile.TemporaryDirectory()`, which makes a folder
and deletes it at the end of the `with` block.

```python
def crash_and_restart(job, crash_after):
    """One crash and one restart, with its own empty bank. Return what happened."""
    with tempfile.TemporaryDirectory() as folder:
        first, _ = attempt(job, crash_after, folder)
        second, printed = attempt(job, 0, folder)
        return {"crash_after": crash_after, "first": first, "second": second, "said": one_line(printed),
                "payments": Bank(folder).payments()[:100], "unpaid": Bank(folder).unpaid()}
```

It's about 40 job runs for each setup, so you don't have to do it. To try one, run `python3 crash_test.py job_once.py`.
It saves `crashes-job_once.json` after every crash, and [code/read_crashes.py](code/read_crashes.py) reads your file if
there is one, and ours if not. **Predict:** which rows have a zero under `Repeats`?

```bash
python3 read_crashes.py
```

```text
Setup                  Crashes  Repeats  Unpaid  Clean  Hit limit
Start again                 20       70       0      0          0
Save before calls           20       70       0      0          0
Save after tools too        19       24       4      0          2
With once                   19        0       4     15          0
With until_done             20        0       0     20          0
```

`Repeats` is payments beyond the first for an order. `Unpaid` is orders with no payment. `Clean` is crashes that ended with
exactly six payments. `Hit limit` is runs where an attempt was stopped at 180 seconds.

- **Start again, and saving before calls, are the same.** Both repeated every payment made before the crash, in all 40
  crashes. The first save changed nothing, because of the batch.
- **`Crashes` isn't always 20.** One run of `job_saved_tools.py` hit the time limit before its crash. One run of
  `job_once.py` finished without reaching payment 5. Neither crashed, so they aren't in the other columns. We ran 20
  and report what happened.
- **`once` took repeats to 0 here.** No bank in those 40 runs held more than six lines.
- **`until_done` took unpaid orders to 0 here.** 20 clean of 20, and all 120 orders paid.

Saving after tools needs a closer look, so read the banks:

```bash
python3 read_crashes.py job_saved_tools
```

```text
after 2: 4 with 1 repeats, 0 unpaid
after 3: 5 with 1 repeats, 0 unpaid
after 4: 4 with 1 repeats, 0 unpaid, 1 with 10 repeats, 0 unpaid
after 5: 4 with 0 repeats, 1 unpaid, 1 with 1 repeats, 0 unpaid
```

14 crashes left one repeat, the payment that landed just before the save. Four left an order unpaid, which is section 7.
And one left 10 repeats. Its bank reads `101 102 103 104 104 105 106 104 105 106 104 105 106 104 105 106`: the restart kept
paying the last three orders until the 180-second limit stopped it. That's the next section.

## 10. The runaway reply

Run 1 in section 4 wrote 77 `issue_refund` calls in one reply. That's the model repeating itself and not stopping.
We've seen it go much further: in earlier testing, not in this chapter's results, one reply in 46 runs wrote about 2,000
calls, and the run went on for a very long time. It's rare, and it's hard to reproduce, so you can't make it happen when
you want to. In this chapter's runs, it showed up as that 77, and the 16-payment bank above. Three runs hit the time limit
in all. For the two with nothing to read, we can't say why, because this was a shared machine and a run can also sit
waiting for the model.

What would stop it? [code/runaway.py](code/runaway.py) hands the code a reply like that, from a fake model, so it needs no
Ollama:

```python
orders = list(ORDERS) * (CALLS // len(ORDERS) + 1)
runaway = Message("assistant", tool_calls=[ToolCall("issue_refund", {"order": order}) for order in orders[:CALLS]])
```

The script runs it with the plain tool, with chapter 17's `LoopGuard`, and with `once`.

```bash
python3 runaway.py
```

```text
plain tool   replies 2, stopped by max_steps: False, payments 2000
LoopGuard    replies 2, stopped by max_steps: False, payments 12
once         replies 2, stopped by max_steps: False, payments 6
```

- **`max_steps` never fires.** It counts replies, and 2,000 calls in one reply is one step.
- **`LoopGuard` limits the damage, but it isn't enough.** It lets each call through twice, so that's 12 payments. And it
  acts only after the reply is written.
- **`once` keeps the bank right**, with six payments.

None of them saves the time. All three act after the whole reply has been written, and writing it is the slow part, so
the fake model can't show that cost. That's why there are two more guards.

The first is the time limit you've used since section 2. It works whatever went wrong. A job stopped this way can be
restarted, and with `once` that's safe.

The second is a cap on the reply itself. Ollama has an option called `num_predict`, the most tokens the model may write in
one reply. [code/job_capped.py](code/job_capped.py) is the finished job with a cap of 60, which is far too low on purpose,
to see what a cap does when it bites. `{**OPTIONS, "num_predict": CAP}` makes a copy of the options with one key added.

```bash
python3 job_capped.py
```

```text
reply: 1 calls, 17 tokens
reply: 2 calls, 60 tokens
reply: 2 calls, 60 tokens
reply: 2 calls, 44 tokens
reply: 0 calls, 2 tokens
DONE
Still unpaid: nothing
```

The reply was cut after two calls, the job carried on, and the finished job still paid everyone. `crash_test.py` on this
job gave 20 crashes, no repeats and no unpaid orders, which you can see with `python3 read_crashes.py job_capped`. So in
these runs a cut reply did no harm, because `once` and `until_done` were there to pick up after it.

Two calls fill 60 tokens here, so a batch of six needs roughly 180. A cap of 512 would leave room, and would stop a reply
at about 17 calls. **That's a sensible cap, not a proven fix.** We've never watched `num_predict` stop a real runaway, because
none turned up in a run that had a cap on. All we've shown is what it does to a normal reply.

## 11. What production uses instead

JSON files and a local bank file are here so you can open them. In production, the checkpoint usually lives in a database,
or you use a workflow engine such as Temporal, which records each step for you. And a real payment service takes an
idempotency key with each request and refuses a repeat itself, which also closes a gap `once` has: two workers could both
ask, both hear "not paid", and both pay.

## What this does and doesn't show

- **One job, one prompt, one 7B model.** The single big batch, the typed `<tool_response>` and the repeating are what
  `qwen2.5:7b` did here. A bigger model may behave differently, so measure yours.
- **The kill is placed at the worst moment, after a payment.** That's what a test should do, but it doesn't tell you how
  often a real crash would land there.
- **20 crashes for each setup isn't many.** `once` and `until_done` each scored 0 here. That means they held in these runs,
  and that the design removes the cause. It doesn't give you a failure rate.
- **We can't separate the two halves of `until_done`.** It names what's left, and it checks again. Our test changed both
  at once. Exercise 6 pulls them apart.
- **`once` only sees what the bank has recorded.** Our bank is a local file, so it's right instantly. A slow real system
  could still be processing a payment when you ask.
- **`num_predict` wasn't shown to stop a runaway.** See section 10.

## Reading errors

The first is the error you met in chapter 20. We triggered the others for real.

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `whitebox.models.ModelError: Couldn't reach Ollama` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| You spelled the job's name wrong | No traceback. `First run: exit code 2`, an empty bank, and every order under `Not paid` | Check the name. Exit code 2 is Python failing to find the file |
| The save was edited by hand and broken | `json.decoder.JSONDecodeError: Invalid control character at: line 1 column 15 (char 14)` | Delete `state.json`. With `once` in place, a fresh start is safe |
| The save isn't a list of messages | `TypeError: string indices must be integers, not 'str'` | Same fix. It isn't a file `Checkpoint` wrote |
| The folder for the job doesn't exist | `FileNotFoundError: [Errno 2] No such file or directory`, on `state.tmp` | Make the folder first |
| `done` uses a different argument name from the tool | No crash. The model gets `Error: <lambda>() got an unexpected keyword argument 'order'` as the tool's result | Name `done`'s arguments the same as the tool's |
| `until_done` found nothing left | `AttributeError: 'NoneType' object has no attribute 'answer'` | It returned `None`, so check `result` first, as `job_until_done.py` does |

## Exercises

From `chapters/27-durable-execution`, open [exercises.py](exercises.py) and complete the five TODOs:

1. `repeats`: count the repeat payments in a bank, as the table does.
2. `resume`: start a job, or carry on from a checkpoint if there is one.
3. `safe_email`: use `once` on a different tool, and work out what counts as the same email.
4. `still_left`: call `until_done`, then find out what never got done.
5. `CallLimit`: a hook that blocks a tool after too many calls in one run, whatever the arguments, for a reply like section 4's 77.

The `sys.path` line at the top of `exercises.py` is provided. It lets the file find the `whitebox` package inside `code/`.

Then check your work from `chapters/27-durable-execution`. These checks use a fake model, so Ollama doesn't need to be
running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in [solutions/exercises.py](solutions/exercises.py).

**Exercise 6, optional: which half did it?** Copy `job_once.py`, and change `AGAIN` so it names the orders the bank shows as
unpaid, with no `until_done`. Run `crash_test.py` on your copy. Do the unpaid orders after payment 5 go away? If they do,
naming them did the work, and the second check is only a safety net. There's no worked answer, because we haven't run it.

## Common mistakes

- **Testing a crash at a kind place.** Our kill comes right after a payment. A crash test that misses that moment proves little.
- **Trusting exit code 0.** The job that paid two people twice finished with 0.
- **Thinking one save per model call means one save per action.** One reply can hold six tool calls.
- **Believing more saves will finish the job.** A crash can always land between the bank and your file.
- **Trusting the checkpoint to say what's been paid.** Ask the real system.
- **Trusting `DONE`.** The model typed "Refunded QC-106." and no tool ran.
- **Ignoring what `until_done` left.** It gives up quietly, so check `left()` afterwards.
- **Running a process with no time limit.** `max_steps` can't stop one long reply.
- **Using `until_done` with nothing to ask.** With no outside record, it has nothing to check.

## Recap

- A killed process leaves no error your code can catch, and a restart with no memory paid 70 repeats in 20 crashes.
- `Checkpoint` saves the conversation through a temporary file and `os.replace`, and `load_messages` reads it back.
- Saving only before model calls changed nothing, because `qwen2.5:7b` put every payment in one reply: 70 again.
- Saving after each tool brought that to one repeat in most crashes, 24 in all. The payment lands just before the save,
  and you can't write to the bank and a file in one step.
- `once` asks the real system first, and repeats went to 0 in 19 crashes here.
- After a crash at payment 5, the model typed a fake `<tool_response>` and stopped, in 8 of 9 crashes, leaving QC-106 unpaid.
- `until_done` asks the bank what's left, and all 20 crashes ended clean here, with 120 of 120 orders paid.
- With no crash at all, the model still repeated payments in 2 of 35 runs. Run 1 made 77.
- A runaway reply is rare. `max_steps` can't stop it. Give every process a time limit, and treat `num_predict` as a sensible
  cap, not a proven fix.

The model chose what to do next. The truth stayed in the bank.

That's the thread of Part 5. `Trim` counts in code, `Memory` keeps her words and the order in code, `Plan` runs each step
in code, and this chapter lets the real system say what happened. In each one, the model made the call, and something
outside it kept the record.

## Where this comes from

Making a repeat harmless with an idempotency key is how payment services work. See
[Stripe's idempotent requests](https://docs.stripe.com/api/idempotent_requests). Recording each step so a run can survive a
crash is what workflow engines such as [Temporal](https://temporal.io) do, and "durable execution" is their name for it.

**Next:** finish the [Part 5 checkpoint](../../checkpoints/part-5/README.md), then Part 6 connects your agent to outside tools with MCP.
