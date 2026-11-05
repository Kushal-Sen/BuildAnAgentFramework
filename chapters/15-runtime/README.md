# Chapter 15: Runtime

**Time:** about 2.5 hours. **You'll build:** an `Agent` you configure once, and can stream, run,
and continue from one conversation to the next.

## Where we are

In chapter 14, you stopped writing tools twice. But `run_agent` is still one function that prints
as it goes. This chapter turns it into something other programs can use. That's the job of a
**runtime**: the part of a framework that runs the agent, and reports what happened.

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. Run the commands in this chapter from `chapters/15-runtime/code`. The first time, install
what this chapter needs:

```bash
python3 -m pip install -r requirements.txt
```

## Feel the problem

[code/old_way.py](code/old_way.py) is provided. It's a copy of chapter 14's `run_agent`, so you've
seen all of it already. It asks a question, then a follow-up:

```python
print(run_agent("What was the coffee revenue on Monday? The files are in the sales folder.",
                model, toolbox, temperature=0))
print(run_agent("And on Tuesday?", model, toolbox, temperature=0))
```

**Predict:** will the model know what "And on Tuesday?" means?

```bash
python3 old_way.py
```

This is real output from `qwen2.5:7b`:

```text
$ python3 old_way.py
[step 1] read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
The coffee revenue on Monday was $120.
I'm not sure what specific information you're asking about on Tuesday. Could you please provide more context or specify what kind of data or information you're interested in regarding Tuesday?
```

Three things are wrong here:

- **It can't continue a conversation.** Each call builds a new list of messages, so the second
  question arrives alone.
- **You wait in silence.** Nothing appears until the model has finished the whole reply.
- **It decides what you see.** The `[step 1]` line is a `print` inside the function. A website
  using this agent couldn't show that step, or hide it. It only gets back a string.

You also pass `model`, `toolbox` and `temperature` on every call. We'll fix all of this, starting
with the silence.

## Stream a reply

In chapter 04, you wrote a generator that gave back one word at a time, and we said models reply
in the same way. Now you'll use that. Every `Model` gets a `stream` method. Open
[code/whitebox/models.py](code/whitebox/models.py):

```python
def stream(self, messages, tools=None, **options):
    """Yield the reply's text in pieces, then the finished Message."""
    reply = self.chat(messages, tools, **options)
    if reply.content:
        yield reply.content
    yield reply
```

This is the default, on the `Model` base class. It calls `chat`, then gives back the text in one
piece, so any model can stream, even `FakeModel`. The last thing it yields is always the finished
`Message`, because that holds any tool calls.

`OllamaModel` replaces this default with a real stream:

```python
def stream(self, messages, tools=None, **options):
    body = self.request_body(messages, tools, options, stream=True)
    response = requests.post(f"{self.url}/api/chat", json=body, timeout=180, stream=True)
    response.raise_for_status()
    text, calls = "", []
    for line in response.iter_lines():
        part = json.loads(line)["message"]
        if part.get("content"):
            text += part["content"]
            yield part["content"]
        calls += part.get("tool_calls") or []
    yield self.from_ollama({"content": text, "tool_calls": calls})
```

- `"stream": True` in the body asks Ollama to send the reply in pieces. The building of that body
  moved into `request_body`, so `chat` and `stream` can share it.
- `stream=True` in `requests.post` tells `requests` not to wait for the whole response.
- `iter_lines` gives you each line as it arrives. Ollama sends one line of JSON per piece.
- Each piece of text is yielded at once, and also saved in `text`.
- A tool call arrives whole, not in pieces, so it's only saved in `calls`.

[code/pieces.py](code/pieces.py) is provided, and shows this happening:

```python
for piece in model.stream(messages, temperature=0):
    if isinstance(piece, Message):
        print("\nThe last thing yielded is the whole Message:")
        print(piece)
    else:
        print(piece, end="|", flush=True)
```

`isinstance(piece, Message)` asks whether a value is a `Message`. Here, it tells the finished
message apart from a piece of text. In `print`, `end="|"` replaces the usual new line, and
`flush=True` shows the text right away, instead of holding it back until the line ends.

```bash
python3 pieces.py
```

```text
$ python3 pieces.py
A| sales| report| is| a| document| that| summarizes| and| analyzes| sales| data|,| including| metrics| such| as| revenue|,| sales| volume|,| and| customer| trends| over| a| specific| period|.| It| helps| businesses| understand| sales| performance| and| make| informed| decisions|.|
The last thing yielded is the whole Message:
Message(role='assistant', content='A sales report is a document that summarizes and analyzes sales data, including metrics such as revenue, sales volume, and customer trends over a specific period. It helps businesses understand sales performance and make informed decisions.', tool_calls=[], tool_name=None)
```

Each `|` marks the end of a piece. On your screen, they appear one at a time.

## From pieces to events

An agent does more than write text. It also calls tools. So a run can't just yield text. Open
[code/whitebox/agent.py](code/whitebox/agent.py), where a new dataclass describes anything that
can happen:

```python
@dataclass
class Event:
    """Something that happened during a run. kind is text, tool_call, tool_result or done."""

    kind: str
    text: str = ""
    call: ToolCall | None = None
    result: Result | None = None
```

And a new class holds the settings you used to pass on every call:

```python
@dataclass
class Agent:
    model: object
    toolbox: Toolbox = field(default_factory=Toolbox)
    system: str = SYSTEM
    max_steps: int = 8
    options: dict = field(default_factory=dict)
```

`run_agent` has become the method `Agent.stream`. It's chapter 12's loop, and it's a generator:

```python
def stream(self, question, history=None):
    """Run the loop, yielding an Event for each thing that happens."""
    messages = list(history) if history else [Message("system", self.system)]
    messages.append(Message("user", question))
    for step in range(1, self.max_steps + 1):
        reply = None
        for piece in self.model.stream(messages, self.toolbox.describe(), **self.options):
            if isinstance(piece, Message):
                reply = piece
            else:
                yield Event("text", piece)
        messages.append(reply)
        if not reply.tool_calls:
            yield Event("done", result=Result(reply.content, messages, step))
            return
        for call in reply.tool_calls:
            yield Event("tool_call", call=call)
            output = self.toolbox.run(call)
            yield Event("tool_result", output, call=call)
            messages.append(Message("tool", output, tool_name=call.name))
    answer = f"Stopped: no answer after {self.max_steps} steps."
    yield Event("done", result=Result(answer, messages, self.max_steps, stopped=True))
```

Compare it with `run_agent`:

- Every `print` has become a `yield`. The framework no longer decides what you see.
- Text goes out as it arrives, and the finished `Message` is kept for the loop.
- `return` inside a generator simply ends it.
- Every run finishes with one `done` event, whichever way it ended.

Now the caller chooses what to show. This is [code/demo.py](code/demo.py):

```python
agent = Agent(model, toolbox, options={"temperature": 0})
for event in agent.stream(QUESTION):
    if event.kind == "text":
        print(event.text, end="", flush=True)
    elif event.kind == "tool_call":
        print(f"[tool] {event.call.name}({event.call.arguments})")
    elif event.kind == "tool_result":
        print(f"    -> {event.text!r}")
print()
```

```bash
python3 demo.py
```

```text
$ python3 demo.py
[tool] list_files({'folder': 'sales'})
    -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[tool] read_file({'path': 'sales/monday.txt'})
    -> 'Coffee: 120\nTea: 80\n'
[tool] read_file({'path': 'sales/tuesday.txt'})
    -> 'Coffee: 150\nTea: 95\n'
[tool] read_file({'path': 'sales/wednesday.txt'})
    -> 'Coffee: 110\nTea: 70\n'
Now, let's extract the coffee revenue from each file and add them up.

Monday's coffee revenue: 120
Tuesday's coffee revenue: 150
Wednesday's coffee revenue: 110

Let's add these numbers to find the total coffee revenue.
[tool] add_numbers({'numbers': [120, 150, 110]})
    -> '380'
The total coffee revenue across all the days in the sales folder is 380.
```

Look at the middle of that output. Before `add_numbers`, the model wrote text, and that text isn't
the answer. It was in every run we tried: 5 of 5 at temperature 0, and 5 of 5 at the default
temperature. All 10 runs reached 380, and in all 10, the streamed text was longer than the final
answer. So if you want only the answer, read it from the `done` event, not from the text.

## Run to the end

Often you don't need live updates. You want the answer, and some facts about the run. That's
`Result`:

```python
@dataclass
class Result:
    answer: str
    messages: list[Message]
    steps: int
    stopped: bool = False
```

And `Agent.run` gets one by reading the stream for you:

```python
def run(self, question, history=None):
    """Run the loop to the end and return the Result."""
    for event in self.stream(question, history):
        if event.kind == "done":
            return event.result
```

There's only one loop in the framework. `run` is built on `stream`, so they can't disagree.

[code/result.py](code/result.py) is provided:

```python
result = agent.run("What was the coffee revenue on Monday? The files are in the sales folder.")
print("Answer: ", result.answer)
print("Steps:  ", result.steps)
print("Stopped:", result.stopped)
print("Messages:", [message.role for message in result.messages])
```

```bash
python3 result.py
```

```text
$ python3 result.py
Answer:  The coffee revenue on Monday was $120.
Steps:   2
Stopped: False
Messages: ['system', 'user', 'assistant', 'tool', 'assistant']
```

Two steps means two calls to the model: one asked for the file, and one answered.

## Continue a conversation

`result.messages` is the whole conversation, and that's all a follow-up needs. Pass it back as
`history`. In `stream`, this line then continues it, instead of starting again:

```python
messages = list(history) if history else [Message("system", self.system)]
```

`list(history)` makes a copy, so a new run can't change an old `Result`. And the `Agent` keeps
nothing between runs. The conversation lives with the caller, so one agent can serve many
conversations.

[code/memory.py](code/memory.py) is provided:

```python
first = agent.run("What was the coffee revenue on Monday? The files are in the sales folder.")
print("First:  ", first.answer)
print("Without:", agent.run("And on Tuesday?").answer)
print("With:   ", agent.run("And on Tuesday?", first.messages).answer)
```

**Predict:** which of the two follow-ups will give 150?

```bash
python3 memory.py
```

```text
$ python3 memory.py
First:   The coffee revenue on Monday was $120.
Without: I'm not sure what specific information you're asking about on Tuesday. Could you please provide more context or specify what kind of data or information you're interested in regarding Tuesday?
With:    The coffee revenue on Tuesday was $150.
```

We ran this 5 times at temperature 0, and 5 times at the default temperature. With history, the
follow-up gave 150 in all 10 runs. Without it, it gave 150 in none of them.

Put that in a loop, and you have a chat program. In [code/chat.py](code/chat.py), `input` waits for
you to type a line, as in chapter 09:

```python
history = None
question = input("You: ")
while question != "quit":
    result = agent.run(question, history)
    history = result.messages
    print("Agent:", result.answer)
    question = input("You: ")
```

```bash
python3 chat.py
```

Here's a real session. Your replies may differ:

```text
$ python3 chat.py
You: What was the coffee revenue on Monday? The files are in the sales folder.
Agent: The coffee revenue on Monday was $120.
You: And on Tuesday?
Agent: The coffee revenue on Tuesday was $150.
You: Add those two numbers together.
Agent: The total revenue from coffee on both Monday and Tuesday was $270.
You: quit
```

## A generator waits for you

One last thing about `stream`, because it surprises people. [code/lazy.py](code/lazy.py) is provided.
It uses a fake model, so you can count the calls:

```python
events = Agent(model, toolbox).stream("How many files are there?")
print("Model calls after stream():", len(model.seen))
print("First event:", next(events).kind)
print("Model calls after one event:", len(model.seen))
print("The rest:", [event.kind for event in events])
print("Model calls at the end:", len(model.seen))
```

**Predict:** how many model calls will there be right after `stream()`?

```bash
python3 lazy.py
```

```text
$ python3 lazy.py
Model calls after stream(): 0
First event: tool_call
Model calls after one event: 1
The rest: ['tool_result', 'text', 'done']
Model calls at the end: 2
```

Calling a generator function runs none of its code. Each time you ask for an event, it runs up to
the next `yield`, then pauses. So reading is what moves the agent forward. If you stop reading,
the agent stops too, and any tools it hasn't reached won't run.

## The framework's own tests

`Agent` replaced `run_agent`, so the tests changed too. From `code/`, run:

```bash
python3 -m pytest tests
```

You should see `17 passed`. These tests use `FakeModel`, so Ollama doesn't need to be running.

## When things go wrong

| What you did | What you see | Fix |
|---|---|---|
| Called `agent.stream(question)` and didn't read it | Nothing happens, and the model isn't called | Loop over it, or call `agent.run` |
| Printed every `text` event as the answer | Notes from the model mixed into the answer | Read the answer from the `done` event |
| Passed `result.answer` as `history` | `AttributeError: 'str' object has no attribute 'role'` | Pass `result.messages` |
| Ollama isn't running | `requests.exceptions.ConnectionError` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |

## Exercises

Open [exercises.py](exercises.py) and complete the five TODOs:

1. `WordModel.stream`: write a new `Model` that streams word by word.
2. `tool_names`: read the tools from a stream of events.
3. `run_live`: show text as it arrives, and return the `Result`.
4. `Conversation.ask`: write a class that remembers, so callers don't have to.
5. `Conversation.transcript`: turn the history into readable lines.

Then check your work from `chapters/15-runtime`, not from `code/`:

```bash
python3 -m pytest test_exercises.py
```

These checks use a fake model, so Ollama doesn't need to be running. You've finished when you see
`5 passed`. Worked answers are in [solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- **Treating all the text as the answer.** The model can write notes between tool calls.
- **Forgetting that a generator is lazy.** Nothing runs until something reads it.
- **Keeping the conversation in the `Agent`.** Then two people sharing an agent would share a
  conversation. Keep it with the caller.
- **Changing `system` on a continued conversation.** The system message is already in `history`,
  so a new one is ignored.

## Recap

- A runtime runs the agent and reports what happened, and leaves the showing to the caller.
- `Model.stream` yields text as it arrives, then the finished `Message`.
- `Agent.stream` yields an `Event` for each thing that happens.
- `Agent.run` reads the stream, and returns a `Result`.
- Passing `result.messages` as `history` continues a conversation.
- A generator only runs while something reads it.

**Next:** chapter 16, where you'll see inside every run.
