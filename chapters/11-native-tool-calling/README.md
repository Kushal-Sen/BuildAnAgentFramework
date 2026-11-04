# Chapter 11: Native tool calling

**Time:** about 1.5 hours. **You'll learn:** how the model API does the job you did by hand in
chapter 10, and what it does better.

## Where we are

In chapter 10, you wrote the tool list into a system prompt, forced the reply's shape with a schema,
and parsed the JSON yourself. It worked, but a joke still made the model read a file.

Model APIs have this job built in. It's called **native tool calling**, and it's the one new idea
in this chapter. Your tools stay the same. Only the way you offer them to the model changes.

## Run it

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. `native.py` is provided, and you haven't seen it yet. Run it first, then we'll open it
piece by piece. From `chapters/11-native-tool-calling/code`:

```bash
python3 native.py "How much coffee was sold on Monday? The file is sales/monday.txt."
```

This is real output from `qwen2.5:7b`. Your wording may differ:

```text
[tool] read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
On Monday, 120 cups of coffee were sold.
```

It's the same result as chapter 10, but `native.py` has no list of tools in its prompt, no `format`
and no `json.loads`.

### Three more questions

Before each one, make a prediction.

**Predict:** in chapter 10, "Tell me a joke." made the model read a file. What will happen now?

```bash
python3 native.py "Tell me a joke."
```

```text
Sure! Here's a joke for you: Why don't scientists trust atoms? Because they make up everything!
```

No `[tool]` line appears. The model chose not to use a tool. We ran it five times each way:

| Version | Asked for a tool it didn't need |
|---|---|
| By hand (chapter 10) | 5/5 |
| Native | 0/5 |

Chapter 10's schema required a tool name, so the model had to pick one. Here, a tool is an option.

**Predict:** this question needs two files. How many tools will the model ask for?

```bash
python3 native.py "What are the sales in sales/monday.txt and sales/tuesday.txt?"
```

```text
[tool] read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
[tool] read_file({'path': 'sales/tuesday.txt'}) -> 'Coffee: 150\nTea: 95\n'
Based on the data from the files:
```

The rest of the reply lists both days. The model asked for both files in one reply, in 10 of 10
runs. Chapter 10's schema had room for only one request, and it read only Monday in 5 of 5 runs.

**Predict:** there's no Friday file. What will the model say?

```bash
python3 native.py "What is in sales/friday.txt?"
```

```text
[tool] read_file({'path': 'sales/friday.txt'}) -> "Error: [Errno 2] No such file or directory: '.../code/workspace/sales/friday.txt'"
It seems that the file 'friday.txt' does not exist in the 'sales' folder. Is there another file you would like to check or any other question regarding the 'sales' folder?
```

We've shortened the folder in that error, and you'll see your full path. The error went back as
text, as in chapter 10, and the model reported it honestly in 10 of 10 runs.

## Open the code

### Describe your tools

Open [code/tools.py](code/tools.py). The functions and `TOOLS` are the same as chapter 10. What's
new is `SCHEMAS`, a list that describes each tool:

```python
schema(
    "read_file",
    "Read a text file.",
    {"path": {"type": "string", "description": "File path, such as sales/monday.txt"}},
    ["path"],
),
```

The four arguments are the tool's name, what it does, its parameters and which parameters are
required. The parameters are a JSON schema, the same thing you wrote in chapter 08. The small
`schema` function wraps them in the shape the API expects.

### Send them with the conversation

Open [code/native.py](code/native.py). This is your `chat` function, with two changes:

```python
def chat(messages, **options):
    """Send the conversation and the tools to the model, and return its whole message."""
    body = {"model": MODEL, "messages": messages, "tools": SCHEMAS, "stream": False, "options": options}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]
```

1. `"tools": SCHEMAS` offers the tools.
2. It returns the whole message, not only its text, because the tool request isn't in the text.

Try removing `"tools": SCHEMAS`, then ask what's in `sales/monday.txt`. In 5 of 5 runs, the model
told us it couldn't read files.

### Read the reply

`peek.py` is provided. It runs three short experiments, and you can read them all in
[code/peek.py](code/peek.py). You don't need to change it. Run it now:

```bash
python3 peek.py
```

The first part prints the whole reply to the Monday question:

```text
1. The whole reply
{
 "role": "assistant",
 "content": "",
 "tool_calls": [
  {
   "id": "call_k90erhjm",
   "function": {
    "index": 0,
    "name": "read_file",
    "arguments": {
     "path": "sales/monday.txt"
    }
   }
  }
 ]
}
```

Your `id` will differ. Notice three things:

- `content` is empty. The model has nothing to say yet.
- `tool_calls` is a list, which is how one reply can ask for two files.
- `arguments` is already a Python dict. There's no `json.loads`.

When the model doesn't want a tool, the `tool_calls` key isn't there at all, so we read it with
`.get`.

### Run the tool, then send the result back

`run_tool` is chapter 10's `dispatch`, reading its name and arguments from the call:

```python
def run_tool(call):
    """Run one tool call. Errors go back to the model so it can recover."""
    name = call["function"]["name"]
    if name not in TOOLS:
        return f"Error: there is no tool called {name}"
    try:
        return str(TOOLS[name](**call["function"]["arguments"]))
    except Exception as error:
        return f"Error: {error}"
```

And this is the whole round trip:

```python
reply = chat(messages, temperature=0)
messages.append(reply)
calls = reply.get("tool_calls")
if not calls:
    return reply["content"]
for call in calls:
    result = run_tool(call)
    print(f"[tool] {call['function']['name']}({call['function']['arguments']}) -> {result!r}")
    messages.append(
        {"role": "tool", "tool_name": call["function"]["name"], "content": result}
    )
reply = chat(messages, temperature=0)
```

Read it in order:

1. Ask the model, and add its reply to the conversation.
2. If it didn't ask for a tool, its text is the answer.
3. Run each tool, and add each result as a message with the role `tool`.
4. Ask again, so the model can use the results.

The role `tool` is new. In chapter 10, you pretended the result was a user message. Now the
conversation says what really happened.

## Side by side

| The job | By hand (`by_hand.py`) | Native (`native.py`) |
|---|---|---|
| Tell the model the tools | Written into `SYSTEM` | `"tools": SCHEMAS` |
| Get a request you can read | `format=REQUEST` | `reply.get("tool_calls")` |
| Read the arguments | `json.loads(reply)` | Already a dict |
| Run the tool | `dispatch(name, arguments)` | `run_tool(call)` |
| Send the result back | A `user` message | A `tool` message |
| No tool needed | It must pick one anyway | It just answers |
| Two tools at once | Only one fits | `tool_calls` is a list |

## Descriptions are prompts

**Predict:** "Read the Monday sales file." doesn't give a path. How will the model find one?

The second part of `peek.py` asks that five times, then asks again with the parameter descriptions
removed:

```text
2. Parameter descriptions
  With:    ['sales/monday.txt', 'sales/monday.txt', 'sales/monday.txt', 'sales/monday.txt', 'sales/monday.txt']
  Without: ['Monday_sales.txt', 'Monday_sales.txt', 'Monday_sales.txt', 'Monday_sales.txt', 'Monday_sales.txt']
```

The only change is removing descriptions like `File path, such as sales/monday.txt`. Without that
example, the model made up a name in 5 of 5 runs. Everything you learned in chapter 08 applies here, because a
tool definition is a prompt.

It also shows that a tool call can be well formed and still wrong. Check what the model asks for.

## Under the hood

Here's the part that opens the box. **A model can still only produce text**, so how does it make a
tool call?

The third part of `peek.py` skips the chat API and sends `/api/generate` the raw text, as you did in
chapter 07. This is what the model really writes:

```text
3. What the model really writes
<tool_call>
{"name": "read_file", "arguments": {"path": "sales/monday.txt"}}
</tool_call>
```

It's text. Look at `raw_prompt` in `peek.py`, and you'll see where it comes from. Each model has a
template, and `qwen2.5:7b`'s template pastes your tools into the system prompt, with instructions on
how to ask for one. You can read yours:

```bash
ollama show qwen2.5:7b --template
```

Ollama then spots the `<tool_call>` tags in the reply and moves the JSON into `tool_calls`.

So native tool calling is what you built in chapter 10: tools described in a prompt, and a request
written as text that gets parsed. Other models use other wording, and this model was trained on its
format. The API just does that work for you.

## One round trip isn't enough

Now try the question from chapter 09.

**Predict:** this needs a folder listing, three files and some addition. What will `native.py` do?

```bash
python3 native.py "What was the total coffee revenue across all the days in the sales folder?"
```

```text
[tool] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
Stopped: the model still wants read_file({'path': 'sales/monday.txt'})
```

It stopped the same way in 10 of 10 runs. The model did the right thing: it listed the folder, then
asked to read the first file. It can't ask for a file until it knows the file's name, so this needs
another step. Our code does one round trip, then it's finished.

## Reading errors

These are real errors:

| What happened | What you see | The fix |
|---|---|---|
| `chat` still returns only the text | `AttributeError: 'str' object has no attribute 'get'` | Return the whole message |
| You looped over `reply.get("tool_calls")` with no check | `TypeError: 'NoneType' object is not iterable` | Check for no calls first |
| The model used a wrong argument name | `Error: read_file() got an unexpected keyword argument 'file'` | Nothing crashes: this goes back to the model as text |

## Exercises

In this chapter's folder, open [exercises.py](exercises.py) and complete the five TODOs:

1. `multiply_schema`: write a tool definition.
2. `requested_calls`: read the tool calls from a reply.
3. `run_tool`: run a call, and return errors as text.
4. `tool_message`: build the message that carries a result.
5. `round_trip`: put it together.

Then check your work. These checks use a fake model, so Ollama doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- **Reading `content` when the model asked for a tool.** It's empty. Check `tool_calls` first.
- **Handling only the first tool call.** `tool_calls` is a list, so run them all.
- **Skipping the reply when you add to `messages`.** In our test, the model still answered correctly
  in 5 of 5 runs, but the conversation no longer shows what it asked for. Keep the record complete.
- **Writing vague descriptions.** The model only knows what your definitions tell it.
- **Trusting a well-formed call.** `Monday_sales.txt` was a valid request for a file that doesn't exist.

## Recap

- You offer tools with `tools=`, using JSON schemas.
- The model asks for them in `tool_calls`, which is a list.
- You run them, and send each result back with the role `tool`.
- The model can choose not to use a tool.
- Tool descriptions are prompts.
- Underneath, a tool call is still text.

## Where this comes from

Function calling became a standard API feature in 2023, when
[OpenAI added it to its API](https://openai.com/index/function-calling-and-other-api-updates/).
Ollama's version is described in its
[tool support post](https://ollama.com/blog/tool-support).

**Next:** chapter 12, where one round trip becomes many.
