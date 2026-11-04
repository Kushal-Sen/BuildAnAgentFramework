"""The checks for exercises.py. You don't need to change this file. They use a fake model,
so Ollama doesn't need to be running."""
from exercises import read_request, request_schema, round_trip, run_tool, safe_run_tool


def double(number):
    return number * 2


def broken():
    raise ValueError("this tool is broken")


TOOLS = {"double": double, "broken": broken}


def test_todo_1_request_schema():
    assert request_schema(["a", "b"]) == {
        "type": "object",
        "properties": {
            "tool": {"type": "string", "enum": ["a", "b"]},
            "arguments": {"type": "object"},
        },
        "required": ["tool", "arguments"],
    }


def test_todo_2_read_request():
    reply = '{"tool": "read_file", "arguments": {"path": "a.txt"}}'
    assert read_request(reply) == ("read_file", {"path": "a.txt"})


def test_todo_3_run_tool():
    assert run_tool(TOOLS, "double", {"number": 4}) == "8"


def test_todo_4_safe_run_tool():
    assert safe_run_tool(TOOLS, "double", {"number": 4}) == "8"
    assert safe_run_tool(TOOLS, "triple", {}) == "Error: there is no tool called triple"
    assert safe_run_tool(TOOLS, "broken", {}) == "Error: this tool is broken"


def test_todo_5_round_trip():
    seen = []

    def fake_chat(messages):
        seen.append([dict(message) for message in messages])
        if len(seen) == 1:
            return '{"tool": "double", "arguments": {"number": 4}}'
        return "The answer is 8."

    assert round_trip("Double 4.", fake_chat, TOOLS) == "The answer is 8."
    assert seen[0] == [{"role": "user", "content": "Double 4."}]
    assert seen[1][1]["role"] == "assistant"
    assert seen[1][1]["content"] == '{"tool": "double", "arguments": {"number": 4}}'
    assert seen[1][2]["role"] == "user"
    assert "8" in seen[1][2]["content"]
