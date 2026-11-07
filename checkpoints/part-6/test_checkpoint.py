"""The checks for checkpoint.py and library_server.py. You don't need to change these. They need no Ollama."""
from checkpoint import ALLOWED, SYSTEM, allowed_tools, build_agent, open_server
from whitebox import Agent, FakeModel, LoopGuard, McpClient, RescueToolCalls, Retry, Tool


def tool(name):
    return Tool(name, "A tool.", {"type": "object", "properties": {}, "required": []}, lambda: "done")


def test_todo_1_book_status():
    with open_server() as server:
        assert "book_status" in [item.name for item in server.tools()]
        assert server.call("book_status", {"title": "EMMA"}) == "on loan until 14 March"


def test_todo_2_unknown_book():
    with open_server() as server:
        answer = server.call("book_status", {"title": "Moby Dick"})
        assert answer.startswith("Error") and "doesn't have Moby Dick" in answer


def test_todo_3_open_server():
    server = open_server()
    assert isinstance(server, McpClient) and server.timeout == 30
    server.__enter__()
    assert server.era == "new"
    server.close()


def test_todo_4_allowed_tools():
    assert [item.name for item in allowed_tools([tool("book_status"), tool("delete_catalogue")])] == ["book_status"]


def test_todo_5_build_agent():
    agent = build_agent(FakeModel([]), [tool("book_status")])
    assert isinstance(agent, Agent)
    assert isinstance(agent.model, Retry) and isinstance(agent.model.model, RescueToolCalls)
    assert agent.system == SYSTEM and agent.options == {"temperature": 0.7}
    assert any(isinstance(hook, LoopGuard) for hook in agent.hooks)
