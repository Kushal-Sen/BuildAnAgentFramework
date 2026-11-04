"""The checks for checkpoint.py. You don't need to change this file."""
from checkpoint import count_tools, find_lines, find_lines_schema, run_agent, run_tool


def tool_call(name, **arguments):
    return {"function": {"name": name, "arguments": arguments}}


def test_todo_1_find_lines():
    assert find_lines("trip/day1.txt", "food") == "Food: 35"
    assert find_lines("trip/day1.txt", "plane") == ""


def test_todo_2_find_lines_schema():
    function = find_lines_schema()["function"]
    assert function["name"] == "find_lines"
    properties = function["parameters"]["properties"]
    assert properties["path"]["type"] == "string" and properties["path"]["description"]
    assert properties["word"]["type"] == "string" and properties["word"]["description"]
    assert sorted(function["parameters"]["required"]) == ["path", "word"]


def test_todo_3_run_tool():
    assert run_tool(tool_call("add_numbers", numbers=[1, 2])) == "3.0"
    assert run_tool(tool_call("fly")).startswith("Error: ")
    assert run_tool(tool_call("find_lines", path="trip/none.txt", word="x")).startswith("Error: ")


def test_todo_4_run_agent():
    replies = [
        {"role": "assistant", "content": "", "tool_calls": [tool_call("add_numbers", numbers=[1, 2])]},
        {"role": "assistant", "content": "It's 3."},
    ]
    seen = []

    def fake_chat(messages):
        seen.append(len(messages))
        return replies[len(seen) - 1]

    answer, messages = run_agent("Add them.", chat=fake_chat)
    assert answer == "It's 3."
    assert seen == [2, 4], "keep the model's reply and the tool result in messages"
    assert messages[3] == {"role": "tool", "tool_name": "add_numbers", "content": "3.0"}

    def stuck_chat(messages):
        return replies[0]

    answer, messages = run_agent("Add them.", chat=stuck_chat, max_steps=3)
    assert answer.startswith("Stopped")
    assert sum(m["role"] == "tool" for m in messages) == 3


def test_todo_5_count_tools():
    messages = [
        {"role": "user", "content": "Hi"},
        {"role": "tool", "tool_name": "find_lines", "content": "a"},
        {"role": "tool", "tool_name": "find_lines", "content": "b"},
        {"role": "tool", "tool_name": "add_numbers", "content": "c"},
    ]
    assert count_tools(messages) == {"find_lines": 2, "add_numbers": 1}
