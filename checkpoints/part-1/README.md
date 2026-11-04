# Part 1 checkpoint: a support ticket classifier

**Time:** about 45 minutes. This checkpoint uses everything from chapters 06 to 08.

You'll build a program that sorts support messages into categories using a model.

Open [checkpoint.py](checkpoint.py) and complete the five TODOs:

1. `ticket_schema`: limit the model to the allowed labels.
2. `ticket_messages`: build the conversation, defining each label clearly.
3. `classify`: call the model and read its label.
4. `classify_all`: write a generator that classifies each ticket.
5. `count_labels`: count how many tickets got each label.

Then check your work from this folder. These checks use a fake model, so Ollama doesn't need to
be running:

```bash
python3 -m pytest test_checkpoint.py
```

You've finished Part 1 when you see `5 passed`.

Finally, try it with the real model. [Start Ollama](../../chapters/00-setup/README.md#step-4-start-ollama),
then run:

```bash
python3 checkpoint.py
```

Worked answers are in [solutions/checkpoint.py](solutions/checkpoint.py).
