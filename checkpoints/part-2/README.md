# Part 2 checkpoint: a trip expenses agent

**Time:** about 45 minutes. This checkpoint uses everything from chapters 09 to 12.

You'll build an agent from its parts, and give it a tool of your own. The `workspace/trip` folder
holds three days of expenses.

Open [checkpoint.py](checkpoint.py) and complete the five TODOs:

1. `find_lines`: write a new tool that finds the lines in a file containing a word.
2. `find_lines_schema`: describe that tool to the model.
3. `run_tool`: run one tool call, and return any error as text.
4. `run_agent`: write the agent loop, with a step limit.
5. `count_tools`: count how many times each tool ran.

Then check your work from this folder. These checks use a fake model, so Ollama doesn't need to
be running:

```bash
python3 -m pytest test_checkpoint.py
```

You've finished Part 2 when you see `5 passed`.

Finally, try it with the real model. [Start Ollama](../../chapters/00-setup/README.md#step-4-start-ollama),
then run:

```bash
python3 checkpoint.py
```

The right answer is 105. Don't stop at one run. Our finished agent reached 105 in 4 of 5 runs. In
the other run it skipped listing the folder, guessed file names, and made up a total. Run yours a
few times, and compare the tool counts it prints.

Worked answers are in [solutions/checkpoint.py](solutions/checkpoint.py).
