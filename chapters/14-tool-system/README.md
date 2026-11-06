# Chapter 14: Tool system

**Time:** about 2.5 hours. **You'll build:** an `@tool` decorator that describes a tool to the model
for you, and a `Toolbox` that checks every call.

## Where we are

In chapter 13, you made the model replaceable. The tools didn't change, and they have a problem you
haven't felt yet: you write each one twice. `read_file` is a Python function, and it's also a
hand-written schema further down the same file. Nothing makes those two agree.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. You'll start in `chapters/13-pluggable-model-layer/code`, then move to
`chapters/14-tool-system/code`.

## 1. Break a tool on purpose

Go to `chapters/13-pluggable-model-layer/code` and open
[sales_tools.py](../13-pluggable-model-layer/code/sales_tools.py). You'll make the kind of small
edit that people make every day: giving a parameter a clearer name. Change `read_file` so that it
says `filename` instead of `path`:

```python
def read_file(filename: str) -> str:
    """Read a text file inside the workspace."""
    return (WORKSPACE / filename).read_text()
```

Leave the schema further down the file as it is:

```python
schema(
    "read_file",
    "Read a text file.",
    {"path": {"type": "string", "description": "File path, such as sales/monday.txt"}},
    ["path"],
),
```

**Predict:** the function now wants `filename`, and the schema still says `path`. What will the model
send? Will the agent work it out?

```bash
python3 demo.py
```

This is real output from `qwen2.5:7b`:

```text
[step 1] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 2] read_file({'path': 'sales/monday.txt'}) -> "Error: read_file() got an unexpected keyword argument 'path'"
[step 3] read_file({'path': 'sales/monday.txt'}) -> "Error: read_file() got an unexpected keyword argument 'path'"
[step 4] read_file({'path': 'sales/monday.txt'}) -> "Error: read_file() got an unexpected keyword argument 'path'"
[step 5] read_file({'path': 'sales/monday.txt'}) -> "Error: read_file() got an unexpected keyword argument 'path'"
[step 6] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 7] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 8] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
Stopped: no answer after 8 steps.
```

The model never sees your Python. It only sees the schema, so it keeps sending `path`. The error even
names the problem, and the model still can't fix it, because the schema is telling it something
else. We ran this 5 more times at temperature 0.7, and none reached 380. Two ran out of steps, and
three gave up and asked for help.

One renamed parameter broke the whole agent, and nothing warned us. Python was happy with the file.
The two copies had simply drifted apart.

**Now undo your edit**, so that chapter 13 works again.

## 2. What Python already knows

Look at what you typed when you wrote that function. The name, the parameters, their types, and
what the function does are all there already. In chapter 03, you saw that a program can read type
hints. So let's see how much of a schema we can get from the function alone.

Now move to `chapters/14-tool-system/code`. Open [code/peek.py](code/peek.py). This script is
provided, and it starts with an ordinary function:

```python
def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read a text file."""
```

Then it prints three things about that function:

```python
print(read_file.__annotations__)
print(read_file.__doc__)
for name, parameter in inspect.signature(read_file).parameters.items():
    required = parameter.default is inspect.Parameter.empty
    print(name, "required" if required else f"default {parameter.default!r}")
```

`inspect` is part of Python. `inspect.signature` describes a function's parameters, and
`inspect.Parameter.empty` is the special value that means "this parameter has no default".

**Predict:** the schema needs a name, a description, each parameter's type, and which parameters are
required. Which of those can't Python tell you?

```bash
python3 peek.py
```

This is the start of the real output:

```text
1. The type hints
{'path': <class 'str'>, 'encoding': <class 'str'>, 'return': <class 'str'>}
2. The docstring
Read a text file.
3. The parameters and their defaults
path required
encoding default 'utf-8'
```

The types come from the hints. The tool's description comes from the docstring. And a parameter
with no default is a required one. Only one thing is missing: a description for each parameter.

## 3. Put the description in the type hint

You can't skip that description. Chapter 11 showed what happens without one: the model made up the
name `Monday_sales.txt` in all 5 runs. So we need somewhere to write it.

`Annotated` is part of Python's `typing` module. `Annotated[str, "some note"]` means "this is a
`str`, and here's a note about it". Python ignores the note, but your program can read it:

```python
def described(path: Annotated[str, "File path, such as sales/monday.txt"]) -> str:
    """Read a text file."""


print(get_type_hints(described, include_extras=True)["path"])
```

`get_type_hints` works like `__annotations__`, and `include_extras=True` tells it to keep the notes.
Part 4 of `peek.py` printed this:

```text
4. A type hint that carries a description
typing.Annotated[str, 'File path, such as sales/monday.txt']
```

Now everything the schema needs is in one place, in the function's own definition.

## 4. Turn a function into a schema

Open [code/whitebox/tools.py](code/whitebox/tools.py). This is the new file in this chapter. It
starts by translating Python types into the words JSON Schema uses:

```python
JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean", dict: "object"}


def json_type(hint):
    """Turn a Python type hint into the JSON Schema that describes it."""
    if hint is list or get_origin(hint) is list:
        items = get_args(hint)
        return {"type": "array", "items": json_type(items[0])} if items else {"type": "array"}
    if hint not in JSON_TYPES:
        raise ValueError(f"Tools can't use the type {hint}")
    return {"type": JSON_TYPES[hint]}
```

Two new helpers from `typing` take a hint apart. For `list[float]`, `get_origin` gives `list`, and
`get_args` gives `(float,)`. Notice that `json_type` calls itself to describe what's inside the list.

The next function uses everything from `peek.py`:

```python
def parameters_of(function):
    """Build the parameters schema from the function's signature."""
    hints = get_type_hints(function, include_extras=True)
    properties, required = {}, []
    for name, parameter in inspect.signature(function).parameters.items():
        hint = hints.get(name)
        if get_origin(hint) is not Annotated:
            raise ValueError(f'{function.__name__}: write {name} as Annotated[type, "description"]')
        kind, description = get_args(hint)
        properties[name] = {**json_type(kind), "description": description}
        if parameter.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": properties, "required": required}
```

For each parameter, it splits the `Annotated` hint into a type and a description, then adds a line
to `properties`. `{**json_type(kind), "description": description}` builds a new dictionary: `**`
copies in everything from the first one, just as it unpacked arguments in chapter 04. If there's no
default, the parameter goes in `required`.

Look at the `raise`. A parameter with no description stops your program before the agent ever runs.
That's on purpose, and you'll test why in section 7.

## 5. The @tool decorator

In chapter 04, you wrote a decorator that stored a function in a dictionary. This one does more. It
gives back a `Tool`:

```python
@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    function: Callable

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


def tool(function):
    """Turn a function into a Tool."""
    if not function.__doc__:
        raise ValueError(f"{function.__name__}: a tool needs a docstring")
    return Tool(function.__name__, inspect.getdoc(function), parameters_of(function), function)
```

`Callable` is the type hint for "something you can call". `__call__` is a special method, like
`__init__`. It runs when you use an object as if it were a function, so `read_file("a.txt")` still
works after decorating. `inspect.getdoc` reads the docstring and tidies its indentation.

Now open [code/sales_tools.py](code/sales_tools.py). Each tool is written once:

```python
@tool
def read_file(path: Annotated[str, "File path, such as sales/monday.txt"]) -> str:
    """Read a text file."""
    return (WORKSPACE / path).read_text()
```

The file went from 55 lines to 28, and there's no `SCHEMAS` list. The last part of `peek.py` printed
what `@tool` built for this function:

```text
5. What @tool built
{
 "type": "function",
 "function": {
  "name": "read_file",
  "description": "Read a text file.",
  "parameters": {
   "type": "object",
   "properties": {
    "path": {
     "type": "string",
     "description": "File path, such as sales/monday.txt"
    }
   },
   "required": [
    "path"
   ]
  }
 }
}
```

That's the shape you wrote by hand in chapter 11. It's a different writer, with the same result.

One detail keeps chapter 13's promise. A `Tool` knows nothing about Ollama. The `"type": "function"`
wrapper is added by a new method in `OllamaModel`, so the provider's format stays at the edge:

```python
def tool_to_ollama(self, tool):
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        },
    }
```

## 6. Break it again

You've seen the agent fail after a small edit. Make the same edit here, in
`chapters/14-tool-system/code/sales_tools.py`:

```python
@tool
def read_file(filename: Annotated[str, "File path, such as sales/monday.txt"]) -> str:
    """Read a text file."""
    return (WORKSPACE / filename).read_text()
```

**Predict:** chapter 13's agent stalled after this edit. What will the model send now?

```bash
python3 demo.py
```

This is real output:

```text
[step 1] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 2] read_file({'filename': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
[step 3] read_file({'filename': 'sales/tuesday.txt'}) -> 'Coffee: 150\nTea: 95\n'
[step 4] read_file({'filename': 'sales/wednesday.txt'}) -> 'Coffee: 110\nTea: 70\n'
[step 5] add_numbers({'numbers': [120, 150, 110]}) -> '380'
The total coffee revenue across all the days in the sales folder is 380.
```

The model sent `filename`, because the schema changed with the function. There's no second copy to
forget.

Does the new system change how well the agent does? Run `python3 five_runs.py`, a provided script
that runs the agent 5 times at temperature 0.7, and counts the answers that reach 380. With this
edit, it reached 380 in 4 of 5 runs. Without it, two batches gave 4 of 5 and 5 of 5. So the tool
system didn't make the model smarter, and it can still fail: one run stopped to announce its next
step, and another ran out of steps. What it removed is one way for you to break the agent.

**Now undo your edit.**

## 7. Why a missing description is an error

Chapter 11's test is worth repeating, because it's the reason `@tool` refuses to work without
descriptions. Open [code/descriptions.py](code/descriptions.py). This script is provided. It asks
the model to read "the Monday sales file", first with this chapter's tools, and then with a copy
that has the descriptions removed:

```python
described = toolbox.describe()
bare = [without_descriptions(tool) for tool in described]
print("With:   ", [first_path(described) for _ in range(5)])
print("Without:", [first_path(bare) for _ in range(5)])
```

**Predict:** which path will the model choose each time?

```bash
python3 descriptions.py
```

This is real output:

```text
With:    ['sales/monday.txt', 'sales/monday.txt', 'sales/monday.txt', 'sales/monday.txt', 'sales/monday.txt']
Without: ['Monday_sales.txt', 'Monday_sales.txt', 'Monday_sales.txt', 'Monday_sales.txt', 'Monday_sales.txt']
```

With descriptions, it was right 5 times out of 5. Without them, it made up a file name 5 times out
of 5. The words `such as sales/monday.txt` did that work. They're part of your prompt, so a framework
shouldn't let you forget them. A plain hint stops the program at once:

```text
ValueError: read_file: write path as Annotated[type, "description"]
```

It's better to find out when the file loads than from a model guessing in the middle of a run.

## 8. The Toolbox

A `Toolbox` holds an agent's tools, and it's the only thing that runs them. The end of
`sales_tools.py` makes one:

```python
toolbox = Toolbox([list_files, read_file, add_numbers])
```

Here's the class, from [code/whitebox/tools.py](code/whitebox/tools.py):

```python
class Toolbox:
    """The tools an agent can use."""

    def __init__(self, tools=()):
        self.tools = {tool.name: tool for tool in tools}

    def describe(self):
        """Describe the tools to a model."""
        return list(self.tools.values())

    def check(self, tool, arguments):
        """Return what's wrong with these arguments, or None."""
        parameters = tool.parameters
        missing = [name for name in parameters["required"] if name not in arguments]
        unknown = [name for name in arguments if name not in parameters["properties"]]
        if missing:
            return f"Error: {tool.name} needs {', '.join(missing)}"
        if unknown:
            return f"Error: {tool.name} doesn't take {', '.join(unknown)}"
        return None

    def run(self, call):
        """Run one tool call. Errors go back to the model as text so it can recover."""
        tool = self.tools.get(call.name)
        if tool is None:
            return f"Error: there is no tool called {call.name}. You have: {', '.join(self.tools)}"
        problem = self.check(tool, call.arguments)
        if problem:
            return problem
        try:
            return str(tool(**call.arguments))
        except Exception as error:
            return f"Error: {error}"
```

`{tool.name: tool for tool in tools}` is a dictionary comprehension. It works like the list
comprehensions in chapter 02, and it builds a dictionary from name to tool. `tools=()` makes an
empty tuple the default, so you can make a `Toolbox` with no tools.

`run` is chapter 12's `run_tool`, plus one new step. Before it calls the function, it compares the
arguments with the schema, using `check`. `run_agent` now takes a `toolbox`, and it calls
`toolbox.describe()` and `toolbox.run(call)`.

Open [code/bad_calls.py](code/bad_calls.py). This script is provided, and it doesn't use the model.
It hands the toolbox five calls, as a confused model might send them:

```python
CALLS = [
    ToolCall("read_file", {"path": "sales/monday.txt"}),
    ToolCall("open_file", {"path": "sales/monday.txt"}),
    ToolCall("read_file", {}),
    ToolCall("read_file", {"path": "sales/monday.txt", "encoding": "utf-8"}),
    ToolCall("read_file", {"path": "sales/friday.txt"}),
]
```

**Predict:** only the first call is correct. Will any of the others crash the program?

```bash
python3 bad_calls.py
```

This is real output. We shortened the long path in the last line to `.../code/`. Yours will show
your own folder:

```text
read_file({'path': 'sales/monday.txt'})
    -> 'Coffee: 120\nTea: 80\n'
open_file({'path': 'sales/monday.txt'})
    -> 'Error: there is no tool called open_file. You have: list_files, read_file, add_numbers'
read_file({})
    -> 'Error: read_file needs path'
read_file({'path': 'sales/monday.txt', 'encoding': 'utf-8'})
    -> "Error: read_file doesn't take encoding"
read_file({'path': 'sales/friday.txt'})
    -> "Error: [Errno 2] No such file or directory: '.../code/workspace/sales/friday.txt'"
```

Nothing crashed. Every failure came back as text, because the model is the one who has to read it.
That's why each message says what to do next. A list of the real tools is more use to a model than
Python's `KeyError`.

Notice what `check` doesn't do. It compares names, not types, so a number sent as `"5"` still reaches
your function. You'll fix that in the exercises.

## 9. Run the framework's tests

From `chapters/14-tool-system/code`:

```bash
python3 -m pytest tests
```

These use `FakeModel`, so Ollama doesn't need to be running. You should see `14 passed`.

## What can go wrong

| What happened | What you see | The fix |
|---|---|---|
| A parameter has a plain hint | `ValueError: read_file: write path as Annotated[type, "description"]` | Give it a type and a description with `Annotated` |
| The docstring is missing | `ValueError: read_file: a tool needs a docstring` | Add a docstring, which becomes the tool's description |
| A type the schema can't describe | `ValueError: Tools can't use the type <class 'set'>` | Use `str`, `int`, `float`, `bool`, `dict` or `list` |
| Ollama isn't running | `requests.exceptions.ConnectionError` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |

## Exercises

These exercises extend the framework, so you won't change anything in `code/whitebox`. Open
[exercises.py](exercises.py), in this chapter's folder, and complete the five TODOs:

1. `average`: write a new tool with `@tool`.
2. `signature_line`: read a `Tool`, and summarize it for a person.
3. `json_type_with_choices`: teach the schema about a fixed set of choices.
4. `StrictToolbox`: check the type of each argument too.
5. `LimitedToolbox`: stop a tool from running too many times.

Three new pieces of Python will help:

- `Literal["low", "high"]` is a type hint that means "one of these strings". You'll turn it into
  chapter 10's `enum`.
- `isinstance(value, str)` asks whether a value is a `str`. You can pass a tuple of types, too.
- In a subclass, `super().check(tool, arguments)` calls the parent class's `check`. That lets you
  add to a method, instead of rewriting it.

Then check your work from this chapter's folder, not from `code`. The `pytest.ini` file there is
provided, and it tells pytest where to find `whitebox`. These checks use a fake model, so Ollama
doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- **Writing a vague description.** `Annotated[str, "A path"]` passes the check, but it doesn't help.
  A good description shows the model an example, such as `sales/monday.txt`.
- **Forgetting `@tool`.** A plain function has no `.name`, so `Toolbox` fails when you create it.
- **Raising errors for the model.** Inside a tool, a raised exception is fine, because `Toolbox.run`
  turns it into text. Make the message useful, because the model will read it.
- **Thinking a check means it's safe.** `check` only compares names. `read_file` can still read any
  path it's given. Chapter 31 deals with that.

## Recap

- A tool written twice can disagree with itself, and neither Python nor the model warns you.
- A function already holds most of its schema: its name, type hints, defaults and docstring.
- `Annotated` adds the one thing missing, a description for each parameter.
- `@tool` builds a `Tool` from the function, so there's only one thing to keep up to date.
- `Toolbox` checks each call against the schema and sends every failure back as text.

## Where this comes from

`Annotated` is described in the [`typing` documentation](https://docs.python.org/3/library/typing.html#typing.Annotated),
and `inspect.signature` in the [`inspect` documentation](https://docs.python.org/3/library/inspect.html#inspect.signature).
The schema format is [JSON Schema](https://json-schema.org/understanding-json-schema/).

**Next:** chapter 15, where you'll turn `run_agent` into a real runtime.
