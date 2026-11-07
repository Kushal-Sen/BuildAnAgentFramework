# Part 6 checkpoint: a library catalogue over MCP

**Time:** about 30 minutes. This checkpoint uses everything from chapters 28 and 29.

Larkfield Library, an invented library, keeps its catalogue in a separate program. You'll finish that server, connect your
agent to it, and decide which of its tools your agent may use. This folder has its own copy of `whitebox`, as it stood at the
end of chapter 29, so you can start here even if your own copy has changed.

Install what this folder needs, from inside your environment:

```bash
python3 -m pip install -r requirements.txt
```

Complete the five TODOs. The first two are in [library_server.py](library_server.py), and the rest are in
[checkpoint.py](checkpoint.py):

1. `book_status`: make it a tool that returns a book's status.
2. `book_status`: raise `ToolError` for a book the library doesn't have.
3. `open_server`: start the server with a `McpClient`.
4. `allowed_tools`: keep only the tools you trust.
5. `build_agent`: give the agent those tools.

Then check your work from this folder. These checks start your real server, but they use a fake model, so Ollama doesn't
need to be running:

```bash
python3 -m pytest test_checkpoint.py
```

You've finished Part 6 when you see `5 passed`.

Finally, try it with the real model. [Start Ollama](../../chapters/00-setup/README.md#step-4-start-ollama), then run:

```bash
python3 checkpoint.py
```

This shows what the server offers and what you allowed, then asks three questions five times each. Before you run it,
predict: which question will do worst?

The server offers `delete_catalogue`, and your agent never sees it. A server chooses what it offers. You choose what your
agent gets.

We ran it three times, for 15 tries at each question:

```text
15 of 15  Is Dune on the shelf?
 3 of 15  When is Emma due back?
15 of 15  Do you have Moby Dick?
```

Yours may differ, and these are small samples. Look at the middle one. Nothing went wrong with MCP: when the model called
the tool, the answer came back right. In the runs we read, the failures never called it. "Emma" is also a person's name, and
one answer said it needed "the title of the book she's borrowing". The protocol worked, and the question failed. Part 3 said
this about evals, and it's still true here: read the answers before you blame the plumbing.

Worked answers are in [solutions/](solutions/). To run them, copy both files over the ones in this folder.
