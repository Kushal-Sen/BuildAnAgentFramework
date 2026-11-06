# Chapter 12: The agent loop

**Time:** about 2 hours. **You'll build:** a working agent in about 60 lines of Python.

## Where we are

In chapter 11, you made one round trip: the model asked for a tool, your code ran it, and the model
used the result. Then `native.py` stopped, because the sales question needs more than one tool, and
the model still wanted another.

This chapter adds the one piece that's missing: a loop.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. You'll work in `chapters/12-agent-loop/code`. `tools.py` is the same file as in chapter 11.

## 1. Run the round trip three times

Open [code/rounds.py](code/rounds.py). `one_round` is the part of chapter 11's `round_trip` that
repeats, as a function. It asks the model, keeps the reply, runs any tools, and keeps the results:

```python
def one_round():
    """Ask the model once. Run any tools it asks for, and keep everything in messages."""
    reply = steady_chat(messages)
    messages.append(reply)
    calls = reply.get("tool_calls")
    if not calls:
        print("Answer:", reply["content"])
        return
    for call in calls:
        result = run_tool(call)
        print(f"{call['function']['name']}({call['function']['arguments']}) -> {result!r}")
        messages.append(
            {"role": "tool", "tool_name": call["function"]["name"], "content": result}
        )
```

`chat` and `run_tool` are chapter 11's, imported from `agent.py`. `steady_chat` just calls `chat`
with `temperature=0`. The script asks our question, then calls `one_round` three times.

**Predict:** the question needs the coffee total from three files. Will three rounds be enough?

```bash
python3 rounds.py
```

This is real output from `qwen2.5:7b`:

```text
list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
read_file({'path': 'sales/tuesday.txt'}) -> 'Coffee: 150\nTea: 95\n'
The conversation now has 8 messages.
```

Three rounds aren't enough, and there's no answer yet. Look at what happened, though. Nobody told
the model the file names. It listed the folder, then used what it found. Each step depended on the
one before.

So how many times should you call `one_round`? You can't know. The model decides as it goes, and a
folder with 30 files would need more rounds than this one. You need to keep going until the model
stops asking for tools.

## 2. Put it in a loop

That gives us the whole idea. An **agent** is a model running in a loop with tools:

1. Send the conversation to the model.
2. If the model asks for tools, run them and add the results to the conversation.
3. Go back to step 1.
4. If the model doesn't ask for a tool, its reply is the final answer.

Open [code/agent.py](code/agent.py). `chat` and `run_tool` are the same as in chapter 11. The new
part is `run_agent`, and the inside of its loop is the round trip you just ran:

```python
def run_agent(question, chat=chat, max_steps=8):
    """Loop until the model answers without asking for a tool."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        reply = chat(messages)
        messages.append(reply)
        calls = reply.get("tool_calls")
        if not calls:
            return reply["content"]
        for call in calls:
            result = run_tool(call)
            print(f"[step {step}] {call['function']['name']}"
                  f"({call['function']['arguments']}) -> {result!r}")
            messages.append(
                {"role": "tool", "tool_name": call["function"]["name"], "content": result}
            )
    return f"Stopped: no answer after {max_steps} steps."
```

There are two ways out of the loop. If the reply has no tool calls, `return` hands back the answer.
If the steps run out, the last line says so.

`chat` is a parameter, so you can pass in a different one. At the bottom of the file, we pass in
`steady_chat`, which keeps the demo repeatable. The exercises pass in a fake model.

```python
def steady_chat(messages):
    """The same chat at temperature 0, so a demo takes the same path each time."""
    return chat(messages, temperature=0)


if __name__ == "__main__":
    print(run_agent(" ".join(sys.argv[1:]), chat=steady_chat))
```

Now run it:

```bash
python3 agent.py "What was the total coffee revenue across all the days in the sales folder?"
```

This is real output. It was the same in 5 of 5 runs here, but yours may take a different path:

```text
[step 1] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 2] read_file({'path': 'sales/monday.txt'}) -> 'Coffee: 120\nTea: 80\n'
[step 3] read_file({'path': 'sales/tuesday.txt'}) -> 'Coffee: 150\nTea: 95\n'
[step 4] read_file({'path': 'sales/wednesday.txt'}) -> 'Coffee: 110\nTea: 70\n'
[step 5] add_numbers({'numbers': [120, 150, 110]}) -> '380.0'
The total coffee revenue across all the days in the sales folder is $380.
```

Nobody told the agent these steps. You've built an agent.

## 3. Why you resend everything

Each call sends the whole conversation, and it gets longer every step. That looks wasteful, so
let's try leaving it out.

Open [code/forgetful.py](code/forgetful.py). It's the same loop, with one change. It builds a fresh
conversation on every step, and it never keeps the replies or the results:

```python
for step in range(1, max_steps + 1):
    messages = [  # A fresh conversation on every step.
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    reply = chat(messages)
```

**Predict:** what will this agent do?

```bash
python3 forgetful.py
```

```text
[step 1] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 2] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 3] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 4] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 5] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 6] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 7] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
[step 8] list_files({'folder': 'sales'}) -> 'monday.txt\ntuesday.txt\nwednesday.txt'
Stopped: no answer after 8 steps.
```

It listed the folder eight times. At temperature 0.7, it did exactly the same in 5 of 5 runs.

You learned why in chapter 07: each call starts with no memory. Every step looks like the first
step to the model, so it makes the first move again. **The conversation is the agent's only memory.**

This run shows two more things:

- **`max_steps` is what stopped it.** Without a limit, this agent would call tools forever.
- **The model's own replies matter too.** We also tried keeping the tool results but not the
  model's replies. None of 5 runs reached an answer: 4 ran out of steps, and 1 returned an empty reply.

## 4. What breaks

The loop is simple, but the model inside it isn't always reliable. So far, we've used temperature
0. Now let's use 0.7 and run the same question several times.

[code/five_runs.py](code/five_runs.py) is a provided measuring tool, so you don't need to read it
closely. It runs your `run_agent` five times with our `SYSTEM` prompt, then five times with a longer
prompt that adds this:

```text
Files are in the workspace. List a folder before reading from it. Do not ask the user for help.
Keep using tools until you can answer.
```

**Predict:** how many of the five runs will reach 380 with each prompt? Will the longer one do better?

```bash
python3 five_runs.py
```

It makes dozens of model calls, so it takes a while. This is real output:

```text
Original prompt
  Run 1: 5 tool calls. Ends: 'all the days in the sales folder is 380.'
  Run 2: 5 tool calls. Ends: 'all the days in the sales folder is 380.'
  Run 3: 5 tool calls. Ends: ' Wednesday) in the sales folder is $380.'
  Run 4: 5 tool calls. Ends: 'all the days in the sales folder is 380.'
  Run 5: 5 tool calls. Ends: 'all the days in the sales folder is 380.'
  Reached 380: 5/5
Longer prompt
  Run 1: 5 tool calls. Ends: 'all the days in the sales folder is 380.'
  Run 2: 6 tool calls. Ends: 'fee revenue across all the days is $380.'
  Run 3: 5 tool calls. Ends: ' Wednesday) in the sales folder is $380.'
  Run 4: 5 tool calls. Ends: 'Monday, Tuesday, and Wednesday) is $380.'
  Run 5: 5 tool calls. Ends: 'll the days in the sales folder is $380.'
  Reached 380: 5/5
```

Both prompts scored 5/5 in this run. But the same script, on the same question, gave 4/5 and 5/5 in the run before it. In that run, one attempt made six tool calls, then gave a wrong total starting with 42. It finished without an error, and it was still wrong. Your scores will vary too.

When we first built this chapter, we ran the same test on three models:

| Model | Download | Original prompt | Longer prompt |
|---|---|---|---|
| `llama3.1:8b` | 4.9 GB | 2/5 | 3/5 |
| `qwen2.5:7b` | 4.7 GB | 5/5 | 4/5 |
| `qwen2.5:14b` | 9.0 GB | 5/5 | 3/5 |

Five runs is a small test, so treat these as a warning, not a ranking. The failures taught
us more than the scores:

- **Guessing:** `llama3.1:8b` tried to read a file called `sales/total_coffee_revenue.txt`, which doesn't exist, then asked the user for help.
- **Running out of steps:** One `qwen2.5:7b` run hit the limit and returned `Stopped: no answer after 8 steps.`
- **Fake tool calls:** `qwen2.5:14b` once wrote a tool call as plain text. Our loop saw no real tool call, so it treated that text as the final answer.
- **Wrong answers:** One `qwen2.5:7b` run made six tool calls and still gave the wrong total. Nothing in the loop can tell.

A bigger model or a longer prompt didn't automatically do better. You'll need a way to
measure this properly, and you'll build one in chapter 18.

## Reading errors

These are real errors:

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `requests.exceptions.ConnectionError` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| `chat` returns text, as in chapter 06 | `AttributeError: 'str' object has no attribute 'get'` | Return the whole message, not just its content |
| The steps ran out | `Stopped: no answer after 8 steps.` | Read the step lines to see where it went round in circles |

## Exercises

In this chapter's folder, open [exercises.py](exercises.py) and complete the five TODOs:

1. `is_final`: check whether a reply is a final answer.
2. `add_results`: run the tool calls, and add their results to the conversation.
3. `run_agent`: write the loop.
4. `run_agent`: stop after `max_steps`.
5. `tools_used`: list the tools the model asked for, so you can read an agent's steps.

Then check your work. These checks use a fake model, so Ollama doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Part 2 checkpoint

You've finished Part 2. Before moving on, complete the
[Part 2 checkpoint](../../checkpoints/part-2/README.md), a trip expenses agent that uses
everything from chapters 09 to 12.

## Common mistakes

- **Forgetting to add the model's reply to `messages`.** One round trip can survive this, but
  the loop can't. In our 5 runs without the replies, none reached an answer.
- **Writing the loop with no limit.** A confused model can call tools forever.
- **Checking only the final answer.** A correct answer can hide a failed tool call, so read
  the steps as well.
- **Judging an agent from one run.** The same agent can pass, then fail.

## Recap

- An agent is a model in a loop with tools.
- The model chooses the next step, and your code runs it.
- You can't know the number of steps in advance, so you loop until there are no tool requests.
- The conversation is the agent's only memory, so you resend all of it.
- Always limit the number of steps.

## Where this comes from

The think, act, observe pattern was popularized by the 2022 paper
[ReAct](https://arxiv.org/abs/2210.03629). Chapter 26 compares it with other planning patterns.

**Next:** chapter 13, where you'll make the model replaceable.
