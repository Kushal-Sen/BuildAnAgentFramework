# Chapter 00: Setup

**Time:** about 1 hour. **You'll build:** a computer that's ready for the whole course.

## What this course is

You'll build an AI agent from scratch. By the end, you'll have your own agent framework and
a coding agent that fixes bugs on its own.

An **AI model** is a program that reads text and predicts a reply. An **agent** is a model
that can also use tools to get work done. You'll learn exactly how that works in later
chapters. For now, you only need to get the tools installed.

## What you'll install

| Tool | What it does |
|---|---|
| Python | Runs all the code in this course |
| Ollama | Runs AI models on your own computer, for free |
| `qwen2.5:7b` | The AI model we use, about a 4.7 GB download |

Your questions stay on your computer, and you don't need an account or API key yet.

## Step 1: Get the course

Open [the course on GitHub](https://github.com/WhiteboxAcademy/BuildAnAgentFramework),
choose **Code > Download ZIP**, and unzip it somewhere easy to find.

## Step 2: Install Python

Install Python 3.12 or newer from [python.org](https://www.python.org/downloads/).
On Windows, tick **Add python.exe to PATH** on the first install screen.

Check that it worked. Open a terminal (Terminal on macOS, PowerShell on Windows) and run:

```bash
python3 --version
```

On Windows, use `python` instead of `python3` throughout this course.

## Step 3: Install Ollama and the model

Install Ollama from [ollama.com/download](https://ollama.com/download), then run:

```bash
ollama pull qwen2.5:7b
```

**Under 8 GB of memory?** Use `qwen2.5:3b` instead. It's enough to start the course, but it
has a real limit. In our test, it passed the setup check but got 0 of 5 runs right on the
multi-step task in chapter 12. If you can, use a computer with at least 8 GB.

## Step 4: Run the setup check

In the terminal, go to `chapters/00-setup/code` in the course folder and run:

```bash
python3 check_setup.py
```

This is real output from a working setup. Your numbers will be different:

```text
PASS  Python: 3.15.0
PASS  Disk space: 48 GB free
PASS  Memory: 24 GB
PASS  Ollama: version 0.34.4
PASS  Model installed: qwen2.5:7b
PASS  Model answers: 'ready'
PASS  Model uses tools: add was called
7/7 passed
```

The last line needs to say `7/7 passed`. The check asks the model two small questions, so it
may take a minute.

If you're using the smaller model, run `python3 check_setup.py qwen2.5:3b`.

## If a check fails

Each failure tells you what to do next. For example, this is what you see when Ollama isn't
running:

```text
PASS  Python: 3.15.0
PASS  Disk space: 48 GB free
PASS  Memory: 24 GB
FAIL  Ollama: Ollama isn't running. Open the Ollama app, or run: ollama serve
SKIP  Model installed: fix the failure above first
SKIP  Model answers: fix the failure above first
SKIP  Model uses tools: fix the failure above first
3/7 passed
```

Fix the first `FAIL` line, then run the check again. `SKIP` means a check couldn't run until
that failure is fixed. There's more help in
[docs/troubleshooting.md](../../docs/troubleshooting.md).

## Exercise

Run the setup check until you see `7/7 passed`. Then talk to your model:

```bash
ollama run qwen2.5:7b "Explain what a terminal is in one sentence."
```

Your reply will be different each time, because models don't always give the same answer.
You've finished this chapter when you get a reply.

## Recap

- You'll build an agent from scratch in this course.
- Ollama runs the AI model on your own computer.
- `check_setup.py` tells you if your computer is ready.

**Next:** chapter 01, where you'll start learning Python.
