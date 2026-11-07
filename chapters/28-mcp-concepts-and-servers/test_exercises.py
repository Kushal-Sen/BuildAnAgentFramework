"""The checks for exercises.py. You don't need to change this file.

They talk to plain_server.py, which is plain Python, so neither Ollama nor mcp needs to be running.
"""
import json
import subprocess
import sys
from pathlib import Path

from exercises import KEY, ME, VERSION, add_to_basket, opening, reply_text, request_line, with_meta

CODE = Path(__file__).parent / "code"


def test_todo_1_request_line():
    line = request_line(7, "tools/list", {})
    assert line.endswith("\n") and line.count("\n") == 1
    assert json.loads(line) == {"jsonrpc": "2.0", "id": 7, "method": "tools/list", "params": {}}
    done = subprocess.run([sys.executable, "plain_server.py"], cwd=CODE, input=line, capture_output=True, text=True,
                          timeout=20)
    assert json.loads(done.stdout)["result"]["tools"][0]["name"] == "get_rota"


def test_todo_2_with_meta():
    params = {"name": "get_rota"}
    made = with_meta(params)
    assert made["name"] == "get_rota"
    assert made["_meta"] == {KEY + "protocolVersion": VERSION, KEY + "clientCapabilities": {}, KEY + "clientInfo": ME}
    assert params == {"name": "get_rota"}


def test_todo_3_reply_text():
    good = {"result": {"content": [{"type": "text", "text": "Friday"}, {"type": "text", "text": "07:00"}]}}
    assert reply_text(json.dumps(good)) == "Friday\n07:00"
    good["result"]["isError"] = False
    assert reply_text(json.dumps(good)) == "Friday\n07:00"
    tool = {"result": {"content": [{"type": "text", "text": "Unknown tool: get_menu"}], "isError": True}}
    assert reply_text(json.dumps(tool)) == "Error: Unknown tool: get_menu"
    protocol = {"error": {"code": -32601, "message": "Method not found"}}
    assert reply_text(json.dumps(protocol)) == "Error: Method not found"


def test_todo_4_opening():
    assert opening({"result": {"supportedVersions": ["2026-07-28"]}}) == "new"
    assert opening({"result": {"supportedVersions": ["2025-11-25", "2026-07-28"]}}) == "new"
    assert opening({"result": {"supportedVersions": ["2099-01-01"]}}) == "old"
    assert opening({"error": {"code": -32602, "message": "Invalid request parameters"}}) == "old"
    assert opening({"error": {"code": -32601, "message": "Method not found"}}) == "old"


def test_todo_5_add_to_basket():
    store = {"basket-1": []}
    assert add_to_basket(store, "basket-1", "flat white") == ["flat white"]
    assert add_to_basket(store, "basket-1", "oat milk") == ["flat white", "oat milk"]
    assert store["basket-1"] == ["flat white", "oat milk"]
    assert add_to_basket(store, "basket-2", "tea") == "Error: no basket called basket-2"
    assert list(store) == ["basket-1"]
    fresh = {"basket-1": ["tea"]}  # Another copy, another store: nothing may leak between them.
    assert add_to_basket(fresh, "basket-1", "toast") == ["tea", "toast"]
