"""The checks for exercises.py. You don't need to change this file.

They use fake models and a fake network, so Ollama doesn't need to be running.
"""
from exercises import BoxyModel, RuleModel, add_boxy, from_boxy, to_boxy
from sales_tools import SCHEMAS, TOOLS
from whitebox import Message, Model, ToolCall, load_model, run_agent


def test_todo_1_to_boxy():
    assert to_boxy(Message("user", "Hi")) == {"role": "user", "content": "Hi"}
    asking = Message("assistant", tool_calls=[ToolCall("add", {"a": 1})])
    assert to_boxy(asking) == {
        "role": "assistant",
        "content": "",
        "calls": [{"tool": "add", "input": {"a": 1}}],
    }
    assert to_boxy(Message("tool", "3", tool_name="add")) == {"role": "tool", "tool": "add", "content": "3"}


def test_todo_2_from_boxy():
    assert from_boxy({"role": "assistant", "content": "Hi"}) == Message("assistant", "Hi")
    reply = from_boxy({"role": "assistant", "content": "", "calls": [{"tool": "add", "input": {"a": 1}}]})
    assert reply == Message("assistant", tool_calls=[ToolCall("add", {"a": 1})])


def test_todo_3_boxy_model_fixes_the_failure_from_welded_py():
    replies = [
        {"role": "assistant", "content": "", "calls": [{"tool": "list_files", "input": {"folder": "sales"}}]},
        {"role": "assistant", "content": "Three files."},
    ]
    sent = []

    def send(body):
        sent.append(body)
        return replies[len(sent) - 1]

    model = BoxyModel("small", send)
    assert isinstance(model, Model), "BoxyModel is a Model"
    assert run_agent("What's in the sales folder?", model, TOOLS, SCHEMAS) == "Three files."
    assert sent[0]["model"] == "small"
    result = sent[1]["messages"][-1]
    assert result["role"] == "tool" and result["tool"] == "list_files"
    assert "monday.txt" in result["content"], "the tool really ran"


def test_todo_4_add_boxy():
    add_boxy()
    model = load_model("boxy/small")
    assert isinstance(model, BoxyModel) and model.name == "small"


def test_todo_5_rule_model_works_in_the_real_loop():
    assert run_agent("Add 2 and 3 and 40", RuleModel(), TOOLS, SCHEMAS).startswith("The total is 45")
