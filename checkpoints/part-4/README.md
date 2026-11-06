# Part 4 checkpoint: a library guide, searched two ways

**Time:** about 45 minutes. This checkpoint uses everything from chapters 19 to 23.

Larkfield Library, an invented library, has a short guide in `workspace/guide`. You'll build two ways of answering
questions about it, then measure them. This folder has its own copy of `whitebox`, as it stood at the end of chapter 23,
so you can start here even if your own copy has changed.

Open [checkpoint.py](checkpoint.py) and complete the five TODOs:

1. `build_chunks`: load the guide, and make chunks that carry their titles.
2. `build_index`: join vector search and keyword search.
3. `build_pipeline`: build the one-search pipeline.
4. `build_agent`: build an agent that searches for itself.
5. `make_cases`: write three eval cases.

Then check your work from this folder. These checks use a fake model and a fake embedder, so Ollama doesn't need to be
running:

```bash
python3 -m pytest test_checkpoint.py
```

You've finished Part 4 when you see `5 passed`.

Finally, measure both with the real models. [Start Ollama](../../chapters/00-setup/README.md#step-4-start-ollama), then
run:

```bash
python3 checkpoint.py
```

This runs each case five times for each setup, so it takes a while. Before you run it, predict: which setup will do
better on "student fee", which needs two facts?

Our pipeline passed 15 of 15 runs, taking 1 step each. Our agent passed 12 of 15, taking 2 steps each, and all three
failures were on "student fee". Yours may differ, and 15 runs is a small sample.

So the setup with half the model calls did better here. We looked at why, in 8 more agent runs:

- Every run searched once, as in chapter 23.
- The 6 that passed had `membership.md` in their results, and the 2 that failed didn't. Those two listed every band.
- The agent rewrites the question into a short query. "late fee per day student" missed the file that says students are
  in Band A. The pipeline searches with the question as typed, and on seven short files, its top 3 held both facts.

That's the last lesson of this part. When both facts are in front of the model, it can join them. So what matters is
whether your search brings them back, and that depends on your documents. In chapter 23, on 95 files, the agent's short
queries helped. Here, they sometimes hurt. Measure on your own documents before you add an agent, and notice the check
that showed this: `excludes("10p")` is why an answer listing every band didn't pass.

Worked answers are in [solutions/checkpoint.py](solutions/checkpoint.py). To run them, copy the file over `checkpoint.py`.
