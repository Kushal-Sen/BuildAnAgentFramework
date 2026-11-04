# Chapter 10: Tool calling by hand

**Time:** about 1.5 hours. **You'll learn:** how a model gets a tool to run, using nothing but
JSON and a Python dict.

## Where we are

In chapter 09, the model asked and you fetched the files. That proved the idea, but an agent can't
wait for you to type. This chapter replaces you with code.

The question from chapter 09 needs several files, so start smaller, with one step of it: **what was
the coffee revenue on Monday?** That takes one tool, and it shows the whole idea.

## Run it

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. `by_hand.py` is provided, and you haven't seen it yet. Run it first, then we'll open it
piece by piece. From `chapters/10-tool-calling-by-hand/code`, run:

```bash
python3 by_hand.py "What was the coffee revenue on Monday?"
```

This is real output from `qwen2.5:7b`:

```text
Model asked for: {"tool": "read_file", "arguments": {"path": "sales/monday.txt"}}
Tool returned: 'Coffee: 120\nTea: 80\n'
Final answer: The coffee revenue on Monday was 120.
```

Three things happened, and the model only did two of them:

1. **The model wrote a request.** It didn't answer. It replied with JSON naming a tool.
2. **Your code ran the tool.** It read the real file.
3. **The model answered,** using the result your code sent back.

This is **tool calling**. The model still only produces text, as you saw in chapter 09. The
difference is that now some of that text is a request your code can read.

**Predict:** which file will the model ask for this time? Then run it:

```bash
python3 by_hand.py "What was the tea revenue on Tuesday?"
```

```text
Model asked for: {"tool": "read_file", "arguments": {"path": "sales/tuesday.txt"}}
Tool returned: 'Coffee: 150\nTea: 95\n'
Final answer: The tea revenue on Tuesday was 95.
```

## Walk through the code

Open [code/by_hand.py](code/by_hand.py). The `chat` function is the one from chapter 08.

### Tools are ordinary functions

```python
def read_file(path: str) -> str:
    """Read a text file inside the workspace."""
    return (WORKSPACE / path).read_text()


TOOLS = {"list_files": list_files, "read_file": read_file, "add_numbers": add_numbers}
```

A **tool** is a function you let the model ask for. There's nothing special about it.

`TOOLS` is the important line. It's a dict from a name to a function. The model can only write
text, so it can write the name `"read_file"`, and this dict turns that name into a function you can
call.

### Tell the model what exists

```python
SYSTEM = """You can use one of these tools:
list_files: list the files in a folder. Arguments: {"folder": "sales"}
read_file: read a text file. Arguments: {"path": "sales/monday.txt"}
add_numbers: add a list of numbers. Arguments: {"numbers": [1, 2]}
Reply with the tool to use and its arguments."""
```

The model can't see your Python. It only knows about the tools you describe in the prompt.

### Get a request your code can read

Your code has to read the model's request, so the request has to be valid JSON.

**Predict:** with only the system message above, how many of five replies will be valid JSON?

We ran it five times at temperature 0.7, using [code/measure.py](code/measure.py), which is provided:

```text
1. No schema
  Valid JSON: 0/5
  A reply: 'To determine the coffee revenue on Monday, we need to read the content of the file containing the sales data for that day.\n\nArguments for the tool:\nread_file: {"path": "sales/monday.txt"}'
```

The model knew what to do, but it wrote a sentence around its request, and `json.loads` can't read
that. You've met this problem and its fix in chapter 08:

```python
REQUEST = {
    "type": "object",
    "properties": {
        "tool": {"type": "string", "enum": list(TOOLS)},
        "arguments": {"type": "object"},
    },
    "required": ["tool", "arguments"],
}
```

```text
2. With the schema
  Valid JSON: 5/5
```

`list(TOOLS)` gives the names in the dict, so `enum` limits `tool` to names that exist. `arguments`
can be any object, because each tool takes different ones.

### Run the tool

```python
def dispatch(name, arguments):
    """Run the tool the model asked for. Errors go back to the model as text."""
    if name not in TOOLS:
        return f"Error: there is no tool called {name}"
    try:
        return str(TOOLS[name](**arguments))
    except Exception as error:
        return f"Error: {error}"
```

Choosing a function from a name like this is called **dispatch**. `TOOLS[name]` finds the function.
`**arguments` unpacks the dict into named arguments, so `{"path": "sales/monday.txt"}` becomes
`read_file(path="sales/monday.txt")`.

The result is always a string, because text is the only thing you can send to a model.

### The round trip

```python
def ask(question, chat=chat, **options):
    """One tool request, one result, one final answer."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    reply = chat(messages, format=REQUEST, **options)
    print("Model asked for:", reply)
    request = json.loads(reply)
    result = dispatch(request["tool"], request["arguments"])
    print("Tool returned:", repr(result))
    messages.append({"role": "assistant", "content": reply})
    messages.append({
        "role": "user",
        "content": f"The tool returned:\n{result}\n\nNow answer my question in one sentence.",
    })
    return chat(messages, **options)
```

There are two calls to the model. The first gets the request, and uses the schema. The second gets
the answer, and doesn't use the schema, because now you want a sentence.

As you learned in chapter 07, a model remembers nothing between calls. So before the second call,
you add the model's request and the tool's result to the conversation, and send all of it again.

`chat=chat` is a default value. Normally `ask` uses the real `chat`, but a test can pass in a fake
model instead.

## When it goes wrong

### A tool fails

**Predict:** there's no file for Sunday. Will this crash, or will the model make up a number?

```bash
python3 by_hand.py "What was the coffee revenue on Sunday?"
```

```text
Model asked for: {"tool": "read_file", "arguments": {"path": "sales/sunday.txt"}}
Tool returned: "Error: [Errno 2] No such file or directory: '/private/tmp/course/code/workspace/sales/sunday.txt'"
Final answer: Based on the available data, the coffee revenue on Sunday is not recorded.
```

Your path and the wording of the answer will differ. `read_file` raised an exception, `dispatch`
caught it, and the error went to the model as text. The model said it couldn't find the data, and
didn't invent a number in 5 of 5 runs.

Without the `try`, the same mistake would crash your program. Treat a tool error as information for
the model, not as the end of the program.

### No tool is needed

**Predict:** a joke needs no tool. What will the model ask for?

```bash
python3 by_hand.py "Tell me a joke."
```

```text
Model asked for: {"tool": "read_file", "arguments": {"path": "sales/monday.txt"}}
Tool returned: 'Coffee: 120\nTea: 80\n'
Final answer: Why did the coffee refuse to go to the party? Because it already had too many commitments!
```

It asked for a tool anyway, in 5 of 5 runs, because the schema requires one. So this version can't
choose to skip tools, even when reading a file makes no sense.

### The model asks for something that doesn't exist

**Predict:** none of our tools can tell you the weather. If we remove the `enum`, what will the model
ask for?

```text
7. No tool fits, without the enum
  {
  "tool": "weather",
  "arguments": {"city": "Kolkata"}
}
  {"tool": "weather", "arguments": {"location": "Kolkata"}}
  {"tool": "weather", "arguments": {"location": "Kolkata"}}
  {
  "tool": "weather",
  "arguments": {"city": "Kolkata"}
}
  { "tool": "weather", "arguments": { "city": "Kolkata" } }
```

The model invented a tool in 5 of 5 runs. With the `enum` back, it could only choose a real name, so
it picked `read_file` in 5 of 5 runs: three times for `sales/monday.txt`, and twice for a weather
file that doesn't exist.

That's chapter 08's lesson again: a schema controls the shape, not the truth. This is why `dispatch`
checks the name, even though the `enum` should prevent a bad one. The model's request is input to
your program, so check it like any other input.

## Reading errors

These are real errors:

| What happened | What you see | The fix |
|---|---|---|
| The reply isn't JSON | `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` | Pass the schema as `format` |
| A tool fails with no `try` around it | `FileNotFoundError: [Errno 2] No such file or directory` | Catch it in `dispatch` |
| The model uses the wrong argument name | `Error: read_file() got an unexpected keyword argument 'file'` | Show the argument names in the system message |
| The model names a tool you don't have | `Error: there is no tool called weather` | Check the name before you look it up |

## Exercises

In this chapter's folder, open [exercises.py](exercises.py) and complete the five TODOs:

1. `request_schema`: write the schema for a tool request.
2. `read_request`: read the tool name and arguments from a reply.
3. `run_tool`: look up a function in a dict and call it.
4. `safe_run_tool`: return errors as text instead of crashing.
5. `round_trip`: do one full round trip.

Then check your work. These checks use a fake model, so Ollama doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- Forgetting to send the result back. The model can't see what your code did.
- Sending only the result in the second call. The model needs the whole conversation. In testing,
  it never answered the question this way, in 5 of 5 runs.
- Passing the schema on the second call too. In testing, it wrote another tool request instead of
  an answer, in 5 of 5 runs.
- Returning a number from a tool without `str`. Messages hold text.
- Letting a tool error crash the program, when the model could have used it.

## Recap

- A model can't run anything. It writes a request, and your code runs it.
- A tool is an ordinary function, and a dict turns its name into a call.
- A schema makes the request something your code can read.
- Results and errors both go back to the model as text.
- The model's request is input, so check it.

## Where this comes from

Teaching a language model to call tools was studied in the 2023
[Toolformer paper](https://arxiv.org/abs/2302.04761). To learn more about the `format` option, read
Ollama's post on [structured outputs](https://ollama.com/blog/structured-outputs).

**Next:** chapter 11, where the model API does this same job for you.
