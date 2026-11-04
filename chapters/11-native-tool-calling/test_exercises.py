"""The checks for exercises.py. You don't need to change this file."""
from exercises import multiply_schema, requested_calls, round_trip, run_tool, tool_message


def call(name, **arguments):
    return {"function": {"name": name, "arguments": arguments}}


def fail():
    raise ValueError("it broke")


def fake_model(*replies):
    """Return a chat function that gives these replies in order, and keeps what it was sent."""
    replies = list(replies)

    def chat(messages):
        chat.seen.append(list(messages))
        return replies.pop(0)

    chat.seen = []
    return chat


def test_todo_1_multiply_schema():
    tool = multiply_schema()
    assert tool["type"] == "function"
    function = tool["function"]
    assert function["name"] == "multiply"
    assert function["description"]
    assert function["parameters"]["type"] == "object"
    assert function["parameters"]["properties"]["numbers"]["type"] == "array"
    assert function["parameters"]["required"] == ["numbers"]


def test_todo_2_requested_calls():
    wanted = call("read_file", path="a.txt")
    assert requested_calls({"role": "assistant", "content": "", "tool_calls": [wanted]}) == [wanted]
    assert requested_calls({"role": "assistant", "content": "Paris"}) == []


def test_todo_3_run_tool():
    tools = {"add": lambda a, b: a + b, "fail": fail}
    assert run_tool(call("add", a=2, b=3), tools) == "5"
    assert run_tool(call("nope"), tools) == "Error: there is no tool called nope"
    assert run_tool(call("fail"), tools) == "Error: it broke"


def test_todo_4_tool_message():
    assert tool_message(call("read_file", path="a.txt"), "hello") == {
        "role": "tool",
        "tool_name": "read_file",
        "content": "hello",
    }


def test_todo_5_round_trip():
    direct = fake_model({"role": "assistant", "content": "Paris"})
    assert round_trip("Capital of France?", direct, {}) == "Paris"
    assert len(direct.seen) == 1

    request = {"role": "assistant", "content": "", "tool_calls": [call("add", a=2, b=3)]}
    chat = fake_model(request, {"role": "assistant", "content": "The sum is 5."})
    assert round_trip("What is 2 + 3?", chat, {"add": lambda a, b: a + b}) == "The sum is 5."
    assert chat.seen[0] == [{"role": "user", "content": "What is 2 + 3?"}]
    assert chat.seen[1][1:] == [
        request,
        {"role": "tool", "tool_name": "add", "content": "5"},
    ]
