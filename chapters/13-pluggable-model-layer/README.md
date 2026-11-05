# Chapter 13: Pluggable model layer

**Time:** about 2.5 hours. **You'll build:** the start of your own framework, called `whitebox`,
where the model is a part you can swap.

## Where we are

Chapter 12 gave you a working agent. It has one hidden problem: every part of it assumes the model
is served by Ollama. This chapter finds that problem, then fixes it, and that fix is the first
piece of a framework.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. You'll work in `chapters/13-pluggable-model-layer/code`.

From this chapter on, `code/` holds a package called `whitebox`. Each chapter in Part 3 adds to it.

## 1. Try another provider

A **provider** is whoever serves the model. So far, that's Ollama. Providers do the same job, but
each has its own format for messages and tool requests.

Open [code/welded.py](code/welded.py). This script is provided. Its `run_agent` and `run_tool` are
chapter 12's, unchanged. The only new part is `boxy_chat`, which stands in for a provider we made
up, called Boxy:

```python
def boxy_chat(messages):
    """Boxy is a provider we made up. It has its own way of asking for a tool."""
    return {
        "role": "assistant",
        "content": "",
        "calls": [{"tool": "list_files", "input": {"folder": "sales"}}],
    }
```

This is a tool request, just like Ollama's, in a different shape. Boxy says `calls` instead of
`tool_calls`, `tool` instead of `name`, and `input` instead of `arguments`.

**Predict:** the script gives this reply to chapter 12's loop. Will the tool run, will Python crash,
or will something else happen?

```bash
python3 welded.py
```

This is the real output:

```text
Answer: ''
```

Nothing crashed, and that's the bad news. The model asked for a tool, and the loop didn't notice. It
looked for `tool_calls`, found none, and decided this was the final answer. So the agent finished
with an empty answer, and no error to tell you why.

## 2. Find what's welded

Why did it fail? Look through `run_tool` and `run_agent` in `welded.py`. Seven lines read or write
Ollama's format:

```python
name = call["function"]["name"]
return str(TOOLS[name](**call["function"]["arguments"]))
calls = reply.get("tool_calls")
return reply["content"]
print(f"[step {step}] {call['function']['name']}"
      f"({call['function']['arguments']}) -> {result!r}")
{"role": "tool", "tool_name": call["function"]["name"], "content": result}
```

To support Boxy, you'd have to change all seven, and then your agent would stop working with Ollama.
The loop and the provider are welded together.

The loop shouldn't care who serves the model. It only needs to know three things: what the model
said, which tools it wants, and how to send back a result. So we'll split the code in two:

- **Your framework** uses its own format, everywhere.
- **One small class per provider** translates between your format and theirs.

The rest of this chapter builds that, one piece at a time.

## 3. Your own message format

Open [code/whitebox/messages.py](code/whitebox/messages.py):

```python
@dataclass
class ToolCall:
    name: str
    arguments: dict


@dataclass
class Message:
    role: str
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_name: str | None = None
```

These are the dataclasses you met in chapter 03. There's nothing here about Ollama or Boxy. A
`ToolCall` is what any tool request comes down to: a name and some arguments.

Now the loop can write `reply.tool_calls` and `call.name`, whoever served the reply. If you mistype
one, Python tells you, instead of quietly finding nothing.

## 4. The Model class

In chapter 03, a `Tool` base class said what every tool must do, and the code that used a tool
didn't care which one it got. This is that idea again. Open
[code/whitebox/models.py](code/whitebox/models.py):

```python
class Model:
    """The shape that every model shares."""

    def chat(self, messages, tools=None, **options):
        raise NotImplementedError
```

That's the whole agreement. A model takes a list of `Message`s, and returns a `Message`. Anything
that does this can drive the agent.

## 5. Translate at the edge

`OllamaModel` is the first real model. Its job is translation. Going out, `to_ollama` turns one of
your messages into Ollama's format:

```python
def to_ollama(self, message):
    data = {"role": message.role, "content": message.content}
    if message.tool_calls:
        data["tool_calls"] = [
            {"function": {"name": call.name, "arguments": call.arguments}}
            for call in message.tool_calls
        ]
    if message.tool_name:
        data["tool_name"] = message.tool_name
    return data
```

Coming back, `from_ollama` does the reverse:

```python
def from_ollama(self, data):
    calls = [
        ToolCall(call["function"]["name"], call["function"]["arguments"])
        for call in data.get("tool_calls") or []
    ]
    return Message("assistant", data.get("content", ""), calls)
```

`data.get("tool_calls") or []` gives you an empty list whether the key is missing or holds nothing.

Then `chat` is chapter 11's `chat` with a translation at each end:

```python
def chat(self, messages, tools=None, **options):
    body = {
        "model": self.name,
        "messages": [self.to_ollama(message) for message in messages],
        "tools": tools or [],
        "stream": False,
        "options": options,
    }
    response = requests.post(f"{self.url}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return self.from_ollama(response.json()["message"])
```

This is called **translating at the edge**. Ollama's format now exists in this one class, right
where your code meets the network.

See it work. [code/peek.py](code/peek.py) is provided. It builds one tool request, translates it to
Ollama's format, and translates it back. This doesn't call the model.

**Predict:** will the message that comes back equal the one that went out?

```bash
python3 peek.py
```

This is the real output:

```text
1. Our format
Message(role='assistant', content='', tool_calls=[ToolCall(name='read_file', arguments={'path': 'sales/monday.txt'})], tool_name=None)
2. Translated for Ollama
{'role': 'assistant', 'content': '', 'tool_calls': [{'function': {'name': 'read_file', 'arguments': {'path': 'sales/monday.txt'}}}]}
3. Translated back
True
```

Dataclasses compare field by field, so `==` is a real check here.

## 6. The loop, unwelded

Open [code/whitebox/agent.py](code/whitebox/agent.py). This is chapter 12's loop, using your format:

```python
def run_agent(question, model, tools, schemas, max_steps=8, **options):
    """Loop until the model answers without asking for a tool."""
    messages = [Message("system", SYSTEM), Message("user", question)]
    for step in range(1, max_steps + 1):
        reply = model.chat(messages, schemas, **options)
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content
        for call in reply.tool_calls:
            result = run_tool(call, tools)
            print(f"[step {step}] {call.name}({call.arguments}) -> {result!r}")
            messages.append(Message("tool", result, tool_name=call.name))
    return f"Stopped: no answer after {max_steps} steps."
```

The steps are the same, but it's shorter and easier to read. All seven of those lines have changed,
and the word Ollama doesn't appear in this file. The model is now an argument, so `run_agent` works
with whatever you pass in.

`whitebox` is a package, like `shop` in chapter 05. Inside a package, a dot means "this same
package", so `from .messages import Message` imports from `whitebox/messages.py`. The
[`__init__.py`](code/whitebox/__init__.py) file imports the main names, which is why other code can
write `from whitebox import Message`.

One piece of Ollama's format is left. [code/sales_tools.py](code/sales_tools.py) is chapter 12's
`tools.py`, and its `SCHEMAS` still use Ollama's shape. Chapter 14 fixes that.

You've changed a lot of code that worked. When you do that, the behavior shouldn't change.

**Predict:** at temperature 0, will the new agent's output match chapter 12's?

```bash
python3 demo.py
```

This is real output from `qwen2.5:7b`:

```text
[step 1] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 2] read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
[step 3] read_file({'path': 'sales/tuesday.txt'}) -> 'Coffee: 150\nTea: 95\n'
[step 4] read_file({'path': 'sales/wednesday.txt'}) -> 'Coffee: 110\nTea: 70\n'
[step 5] add_numbers({'numbers': [120, 150, 110]}) -> '380.0'
The total coffee revenue across all the days in the sales folder is $380.
```

It matches chapter 12's output line for line. We ran it 5 times, and all 5 matched. The model
sees the same conversation as before, because the translation puts it back into Ollama's format.

## 7. A model that isn't a model

In chapter 05, you passed in a fake `get` so your tests could run without a network. Now that the
model is an argument, the same trick works here:

```python
class FakeModel(Model):
    """Gives back replies you wrote in advance, and remembers what it was sent."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.seen = []

    def chat(self, messages, tools=None, **options):
        self.seen.append(list(messages))
        return self.replies.pop(0)
```

`pop(0)` removes the first item from a list and gives it back, so each call gets the next reply.
`list(messages)` saves a copy, because the loop keeps adding to the original.

[code/swap.py](code/swap.py) is provided. It sends one question through the same `run_agent`, first
with `OllamaModel`, then with a `FakeModel`:

```python
real = OllamaModel("qwen2.5:7b")
fake = FakeModel([
    Message("assistant", tool_calls=[ToolCall("read_file", {"path": "sales/monday.txt"})]),
    Message("assistant", "This answer was written in advance."),
])
```

**Predict:** the fake has no AI in it. Will the tool really run?

```bash
python3 swap.py
```

This is the real output:

```text
With OllamaModel
[step 1] read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
According to the file, the coffee revenue on Monday was $120.

With FakeModel
[step 1] read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
This answer was written in advance.
The fake was called 2 times.
On its last call, it saw 4 messages.
```

The tool ran both times. The loop can't tell the two apart, which is the whole point. The output was
the same in 5 of 5 runs here.

This gives you something you didn't have before: tests for your agent that need no model, so they
run instantly and pass or fail the same way every time. Open
[code/tests/test_agent.py](code/tests/test_agent.py):

```python
def test_the_loop_runs_a_tool_then_answers():
    model = FakeModel([
        Message("assistant", tool_calls=[ToolCall("double", {"number": 4})]),
        Message("assistant", "It's 8."),
    ])
    assert run_agent("Double 4.", model, {"double": double}, []) == "It's 8."
    assert model.seen[1][-1] == Message("tool", "8", tool_name="double")
```

The last line uses `seen` to check what the loop sent the model. Run the tests from `code/`:

```bash
python3 -m pytest tests
```

You should see `5 passed`. Ollama doesn't need to be running for these.

## 8. Choose a model by name

Your code shouldn't have to change when you change model. So `load_model` builds one from a short
string, such as `ollama/qwen2.5:7b`:

```python
PROVIDERS = {"ollama": OllamaModel}


def load_model(spec=None):
    """Build a model from a "provider/name" string, or from the MODEL setting."""
    spec = spec or os.environ.get("MODEL", DEFAULT_MODEL)
    provider, _, name = spec.partition("/")
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}. Choose from {sorted(PROVIDERS)}.")
    return PROVIDERS[provider](name)
```

Three things here are new:

- **`os.environ`** holds your computer's environment variables, which are settings that live outside
  your code. `.get` is the same one you use on any dictionary, so `MODEL` wins if it's set, and
  otherwise you get the default. Setting one differs between Windows, macOS and Linux, so in this
  course we'll pass the name on the command line instead.
- **`partition("/")`** splits a string at the first `/` into three parts: before, the `/` itself, and
  after. So `ollama/qwen2.5:7b` gives `ollama`, `/` and `qwen2.5:7b`. `_` is the usual name for a
  value you don't need.
- **`PROVIDERS` holds classes.** A class is a value, just as a function is, so
  `PROVIDERS[provider](name)` finds the class, then calls it. It's the same as
  `OllamaModel("qwen2.5:7b")`. It's chapter 10's `TOOLS` dictionary again, with classes instead of
  functions.

`demo.py` passes its command-line argument to `load_model`:

```python
model = load_model(sys.argv[1] if len(sys.argv) > 1 else None)
print(run_agent(QUESTION, model, TOOLS, SCHEMAS, temperature=0))
```

**Predict:** what happens with a provider that doesn't exist? And with a real provider, but a model
you've never downloaded?

```bash
python3 demo.py nobody/model
python3 demo.py ollama/not-a-model
```

The first ends with this real output:

```text
ValueError: Unknown provider 'nobody'. Choose from ['ollama'].
```

The second gets as far as asking Ollama, and ends with this:

```text
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: http://127.0.0.1:11434/api/chat
```

Two different failures. `load_model` caught the first itself, with a message that says what to do.
The second is a raw error from Ollama, which is less friendly. You'll deal with errors like that in
chapter 17.

If you've downloaded another model, try it with `python3 demo.py ollama/<its name>`. Run
`ollama list` to see what you have. No code changes, though the answer may. As you saw in chapter 12,
models behave differently in the same loop.

## What breaks

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `requests.exceptions.ConnectionError` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| You ran pytest from inside `tests/` | `ModuleNotFoundError: No module named 'whitebox'` | Run `python3 -m pytest tests` from `code/` |
| The model isn't downloaded | `404 Client Error: Not Found` | Check the name with `ollama list` |
| A `FakeModel` ran out of replies | `IndexError: pop from empty list` | The loop made more calls than you scripted, so add a reply |

## Exercises

In this chapter's folder, open [exercises.py](exercises.py). You'll fix the failure from the start
of this chapter by adding Boxy to your framework, without changing `whitebox` at all:

1. `to_boxy`: translate a `Message` into Boxy's format.
2. `from_boxy`: translate Boxy's reply into a `Message`.
3. `BoxyModel`: write a new `Model` subclass. Its check runs the real `run_agent`, on the reply that
   defeated chapter 12's loop.
4. `add_boxy`: add it to `PROVIDERS`, so `load_model("boxy/small")` works.
5. `RuleModel`: write a `Model` with no AI in it at all, and watch the loop run it.

Then check your work from the chapter folder, not from `code/`. These checks use fake models, so
Ollama doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. The provided `conftest.py` file lets pytest find `whitebox`
in `code/`. Worked answers are in [solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- **Letting a provider's format leak out of its class.** If you write `["function"]` outside
  `OllamaModel`, the weld is back.
- **Changing the loop to add a provider.** A new provider is a new `Model` subclass. The loop stays
  as it is.
- **Trusting a fake too far.** A `FakeModel` tests your code, not the model. It can't tell you
  whether a real model will reach 380.
- **Forgetting that a fake is scripted.** It gives its replies in order, whatever you send it.

## Recap

- A provider's format shouldn't reach your agent loop.
- Your framework has its own format: `Message` and `ToolCall`.
- `Model` is the agreement. Anything with a `chat` method that takes and returns `Message`s can
  drive the agent.
- Each provider gets one class, which translates at the edge.
- `FakeModel` lets you test the agent with no model running.
- `load_model` picks a model from a name, so changing model doesn't change your code.

## Where this comes from

A class that translates one interface into another is known as the
[adapter pattern](https://en.wikipedia.org/wiki/Adapter_pattern). `OllamaModel` is an adapter.

**Next:** chapter 14, where each tool gets described only once.
