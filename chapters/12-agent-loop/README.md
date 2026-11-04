# Chapter 12: The agent loop

**Time:** about 2 hours. **You'll build:** a working agent in about 60 lines of Python.

## Where we are

In chapter 11, the model asked for one tool, your code ran it, and the model used the
result to answer. That's enough for "What is 2 + 2?", but most real tasks take several
steps, and each step depends on the one before. You can't read a file until you know
its name.

This chapter adds the piece that handles that: a loop.

## The idea

An agent is a model running in a loop with tools:

1. Send the conversation to the model.
2. If the model asks for tools, run them and add the results to the conversation.
3. Go back to step 1.
4. If the model doesn't ask for a tool, its reply is the final answer.

The model decides what to do next. Your code does the work and keeps the conversation.
The model remembers nothing between calls, so you resend the whole conversation each time.

## Run it

Make sure Ollama is running, then from `chapters/12-agent-loop/code`:

```bash
python3 agent.py "What was the total coffee revenue across all the days in the sales folder?"
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

Nobody told the agent these steps. It listed the folder, used those names to read each
file, then added the numbers. Your run may take a different path, because models vary.

## Walk through the code

Open [code/agent.py](code/agent.py). The loop is in `run_agent`:

```python
for step in range(1, max_steps + 1):
    reply = chat(messages)
    messages.append(reply)
    calls = reply.get("tool_calls")
    if not calls:
        return reply["content"]
    for call in calls:
        result = run_tool(call)
        messages.append(
            {"role": "tool", "tool_name": call["function"]["name"], "content": result}
        )
return f"Stopped: no answer after {max_steps} steps."
```

Three details make this safe to run:

- **`max_steps` stops runaway loops.** Without it, a confused model could call tools forever.
- **`run_tool` returns errors as text.** A failed tool doesn't crash the agent. The model
  reads the error and can try something else.
- **`chat` is a parameter.** You can pass in a fake model, which is how the exercises run
  without Ollama.

## What breaks

The loop is simple, but the model inside it isn't always reliable. We ran the same question
five times per setting, at temperature 0.7, and counted the runs that reached 380:

| Model | Download | Original prompt | Longer prompt |
|---|---|---|---|
| `llama3.1:8b` | 4.9 GB | 2/5 | 3/5 |
| `qwen2.5:7b` | 4.7 GB | 5/5 | 4/5 |
| `qwen2.5:14b` | 9.0 GB | 5/5 | 3/5 |

Five runs is a small test, so treat these as a warning, not a ranking. The failures taught
us more than the scores:

- **Guessing:** `llama3.1:8b` tried to read a file called `sales/total_coffee_revenue.txt`,
  which doesn't exist, then asked the user for help.
- **Running out of steps:** one `qwen2.5:7b` run hit the limit and returned
  `Stopped: no answer after 8 steps.`
- **Fake tool calls:** `qwen2.5:14b` once wrote a tool call as plain text. Our loop saw no
  real tool call, so it treated that text as the final answer.

A bigger model or a longer prompt didn't automatically do better. You'll need a way to
measure this properly, and you'll build one in chapter 18.

## Exercises

Open [exercises.py](exercises.py) and complete the three TODOs:

1. Return an error if the model asks for a tool that doesn't exist.
2. Return an error if a tool raises an exception.
3. Stop after `max_steps`.

Then check your work. Ollama doesn't need to be running:

```bash
python3 exercises.py
```

You've finished when you see `3/3 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- **Forgetting to add the model's reply to `messages`.** The model then can't see its own
  tool request, and the conversation stops making sense.
- **Letting tool errors crash the program.** Return them instead, so the model can recover.
- **Checking only the final answer.** A correct answer can hide a failed tool call, so read
  the steps as well.

## Recap

- An agent is a model in a loop with tools.
- The model chooses the next step, and your code runs it.
- The conversation is the agent's only memory.
- Always limit the number of steps.
- Errors go back to the model as text.

## Where this comes from

The think, act, observe pattern was popularized by the 2022 paper
[ReAct](https://arxiv.org/abs/2210.03629). Chapter 25 compares it with other planning patterns.

**Next:** chapter 13, where you'll make the model replaceable.
