# Part 5 checkpoint: a desk job that survives a crash

**Time:** about 45 minutes. This checkpoint uses everything from chapters 24 to 27.

Larkfield Library, an invented library, is returning five members' deposits. Your agent has to remember who it's
talking to, stay inside its budget, and survive being killed halfway through, without paying anyone twice or missing
anyone. This folder has its own copy of `whitebox`, as it stood at the end of chapter 27, so you can start here even if
your own copy has changed.

Open [checkpoint.py](checkpoint.py) and complete the five TODOs:

1. `build_agent`: build an agent with memory, a token budget and save points.
2. `safe_tool`: make the deposit tool safe to repeat, by asking the bank.
3. `left_to_pay`: work out who the bank hasn't paid.
4. `finish`: pick up any saved run, and keep going until the bank says it's done.
5. `build_planner`: build a planner.

Then check your work from this folder. These checks use a fake model and a fake embedder, so Ollama doesn't need to be
running:

```bash
python3 -m pytest test_checkpoint.py
```

You've finished Part 5 when you see `6 passed`. TODO 4 has two checks.

Finally, crash it for real. [Start Ollama](../../chapters/00-setup/README.md#step-4-start-ollama), then run:

```bash
python3 checkpoint.py
```

This kills the job right after a payment, starts it again, and reads the bank, five times. Each attempt runs as its own
process and has a time limit of 180 seconds. Before you run it, predict: how many of the five will end with every member
paid exactly once?

We ran it three times, and all 15 crashes ended clean: five payments, no repeats, no one unpaid. Yours may differ, and 15
is a small sample. Chapter 27 is why you shouldn't relax about that number. Its setups that looked fine in a few runs
failed in others, and its rarest failures only showed up after dozens of crashes.

Look at what you built. The model chose what to do, and your code held everything that had to be true: the notes in the
person's own words, the order they were saved, the budget, the save point, and the bank's record of who was paid. That's
the lesson of this part. **Let the model make the judgement call, and keep the facts, the order and the truth in code.**

Worked answers are in [solutions/checkpoint.py](solutions/checkpoint.py). To run them, copy the file over `checkpoint.py`.
