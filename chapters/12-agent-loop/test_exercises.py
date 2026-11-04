"""The checks for exercises.py. You don't need to change this file.

They use a fake model that gives scripted replies, so Ollama doesn't need to be running.
"""
from exercises import add_results, is_final, run_agent, tools_used


def tool_call(name, **arguments):
    return {"function": {"name": name, "arguments": arguments}}


def asks_for(*calls):
    return {"role": "assistant", "content": "", "tool_calls": list(calls)}


def answers(text):
    return {"role": "assistant", "content": text}


def fake_model(*replies):
    """Return a chat function that gives each reply in turn, and records what it was sent."""
    remaining = list(replies)

    def chat(messages):
        chat.sent.append(list(messages))
        return remaining.pop(0)

    chat.sent = []
    return chat


def test_todo_1_is_final():
    assert is_final(answers("380")) is True
    assert is_final({"role": "assistant", "content": "380", "tool_calls": []}) is True
    assert is_final(asks_for(tool_call("add", a=1, b=2))) is False


def test_todo_2_add_results():
    messages = []
    add_results(messages, [tool_call("add", a=1, b=2), tool_call("missing")])
    assert messages == [
        {"role": "tool", "tool_name": "add", "content": "3"},
        {"role": "tool", "tool_name": "missing", "content": "Error: there is no tool called missing"},
    ]


def test_todo_3_run_agent():
    first = asks_for(tool_call("add", a=1, b=2))
    chat = fake_model(first, answers("The total is 3."))
    assert run_agent("What is 1 + 2?", chat) == "The total is 3."
    assert chat.sent[0] == [{"role": "user", "content": "What is 1 + 2?"}]
    assert chat.sent[1] == [
        {"role": "user", "content": "What is 1 + 2?"},
        first,
        {"role": "tool", "tool_name": "add", "content": "3"},
    ]


def test_todo_4_step_limit():
    replies = [asks_for(tool_call("add", a=1, b=2)) for _ in range(10)]
    chat = fake_model(*replies)
    assert run_agent("Keep going", chat, max_steps=3) == "Stopped: no answer after 3 steps."
    assert len(chat.sent) == 3


def test_todo_5_tools_used():
    messages = [
        {"role": "user", "content": "What is in the folder?"},
        asks_for(tool_call("list_files", folder="sales")),
        {"role": "tool", "tool_name": "list_files", "content": "monday.txt"},
        asks_for(tool_call("read_file", path="a.txt"), tool_call("read_file", path="b.txt")),
        answers("Done."),
    ]
    assert tools_used(messages) == ["list_files", "read_file", "read_file"]
