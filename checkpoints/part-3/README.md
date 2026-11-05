# Part 3 checkpoint: a trip expenses agent, on your framework

**Time:** about 45 minutes. This checkpoint uses everything from chapters 13 to 18.

In the Part 2 checkpoint, you built a trip expenses agent from scratch. Now you'll rebuild it on
the framework, and measure it. This folder has its own copy of `whitebox`, as it stood at the end
of chapter 18, so you can start here even if your own copy has changed.

Open [checkpoint.py](checkpoint.py) and complete the five TODOs:

1. `find_lines`: write a tool with `@tool`.
2. `CountingModel`: wrap a model, and count its calls.
3. `ToolCounter`: write a hook that counts tool calls.
4. `build_agent`: put the model, tools, retries and hooks together.
5. `make_cases`: write two eval cases.

Then check your work from this folder. These checks use a fake model, so Ollama doesn't need to
be running:

```bash
python3 -m pytest test_checkpoint.py
```

You've finished Part 3 when you see `5 passed`.

Finally, measure it with the real model. [Start Ollama](../../chapters/00-setup/README.md#step-4-start-ollama),
then run:

```bash
python3 checkpoint.py
```

This runs each case five times, so it takes a while. Our finished agent passed 9 of 10 runs, using
57 model calls. Yours will differ. Ten runs is a small sample, so don't read much into a difference
of one.

Worked answers are in [solutions/checkpoint.py](solutions/checkpoint.py). To run them, copy the file
over `checkpoint.py`.
