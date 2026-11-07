"""A server in plain Python, with no SDK. It's only a loop: read a line, work out a reply, write a line."""
import json
import sys

TOOLS = [{
    "name": "get_rota",
    "description": "Look up someone's next shift.",
    "inputSchema": {"type": "object", "properties": {"staff_number": {"type": "string"}}},
}]

for line in sys.stdin:
    request = json.loads(line)
    if request["method"] == "tools/list":
        result = {"tools": TOOLS}
    else:
        result = {"content": [{"type": "text", "text": "Your next shift is Friday at 07:00."}]}
    print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)
