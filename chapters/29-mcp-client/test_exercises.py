"""The checks for exercises.py. You don't need to change this file.

They use a fake model, FakeEmbedder and the plain test server in code/tests, so neither Ollama nor mcp needs to be running.
"""
import sys
from pathlib import Path

import pytest

from exercises import closest_tools, connect_all, named_tools, read_reply, to_tool
from whitebox import Agent, FakeEmbedder, FakeModel, McpClient, McpError, Message, Tool, ToolCall, Toolbox

FAKE = str(Path(__file__).parent / "code" / "tests" / "fake_mcp_server.py")


def server(kind):
    return [sys.executable, FAKE, kind]


def pretend(name, description=""):
    return Tool(name, description, {"type": "object", "properties": {}, "required": []}, lambda: name)


def test_todo_1_read_reply():
    lines = ['starting up\n', '{"id": 1, "result": "old"}\n', '  debug: hello  \n', '{"id": 2, "result": "mine"}\n', 'later\n']
    assert read_reply(lines, 2) == ({"id": 2, "result": "mine"}, ["starting up", "debug: hello"])
    assert read_reply(['{"id": 7, "result": {}}\n'], 7) == ({"id": 7, "result": {}}, [])
    with pytest.raises(McpError, match="stopped"):
        read_reply(['{"id": 1, "result": {}}\n', "noise\n"], 2)


def test_todo_2_to_tool():
    seen = []

    def call(name, arguments):
        seen.append((name, arguments))
        return "42"

    item = {"name": "double", "inputSchema": {"type": "object", "properties": {"number": {"type": "integer"}}}}
    made = to_tool(item, call)
    assert isinstance(made, Tool) and made.name == "double" and made.description == ""
    assert made.parameters["required"] == [] and "required" not in item["inputSchema"]
    assert made(number=21) == "42" and seen == [("double", {"number": 21})]
    kept = to_tool({"name": "a", "description": "b", "inputSchema": {"properties": {}, "required": ["x"]}}, call)
    assert kept.description == "b" and kept.parameters["required"] == ["x"]

    with McpClient(server("new"), timeout=5) as client:  # A real conversation, then a real agent loop.
        client_item = client.result("tools/list")["tools"][0]
        model = FakeModel([Message("assistant", tool_calls=[ToolCall("double", {"number": 4})]), Message("assistant", "8")])
        result = Agent(model, Toolbox([to_tool(client_item, client.call)])).run("Double 4")
        assert result.messages[-2].content == "8"


def test_todo_3_connect_all():
    commands = {"good": server("new"), "dead": server("dies"), "quiet": server("silent"), "older": server("old"),
                "missing": ["/no/such/program"]}
    clients, tools, problems = connect_all(commands, timeout=1)
    try:
        assert [client.era for client in clients] == ["new", "old"]
        assert [item.name for item in tools] == ["double", "double"]
        assert tools[0](number=2) == "4" and tools[1](number=3) == "6"
        assert problems[:2] == ["dead: The server has stopped", "quiet: No reply after 1 seconds"]
        assert len(problems) == 3 and problems[2].startswith("missing: Couldn't start the server")
    finally:
        for client in clients:
            client.close()


def test_todo_4_named_tools():
    one, two = pretend("search", "Search the rota."), pretend("search", "Search the loyalty cards.")
    joined = named_tools({"rota": [one], "loyalty": [two]})
    assert [item.name for item in joined] == ["rota_search", "loyalty_search"]
    assert [item.description for item in joined] == ["Search the rota.", "Search the loyalty cards."]
    assert joined[0].parameters is one.parameters and joined[0].function is one.function
    assert one.name == "search" and two.name == "search"
    assert len(Toolbox(joined).tools) == 2
    assert len(Toolbox([one, two]).tools) == 1  # Why this exercise exists.


def test_todo_5_closest_tools():
    tools = [pretend("till", "open the till and count the float"), pretend("rota", "look up a shift on the staff rota"),
             pretend("waste", "record food thrown in the bin"), pretend("fault", "report a broken grinder to the contractor")]
    embedder = FakeEmbedder(size=512)
    assert [item.name for item in closest_tools(tools, "the grinder is broken", 1, embedder)] == ["fault"]
    picked = closest_tools(tools, "which shift is on the rota", 2, embedder)
    assert len(picked) == 2 and picked[0].name == "rota"
    assert len(closest_tools(tools, "anything", 9, embedder)) == 4
    assert [item.name for item in tools] == ["till", "rota", "waste", "fault"]
