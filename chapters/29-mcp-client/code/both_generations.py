"""Print every line McpClient writes and reads. Pass the older environment's Python to try the older server too."""
import json
import sys

from whitebox import McpClient

UNUSED = ("_meta", "cacheScope", "capabilities", "instructions", "resultType", "serverInfo", "ttlMs")


def short(message):
    """One message on one line, without the fields that are the same every time or that we don't use."""
    shown = {key: value for key, value in message.items() if key != "jsonrpc"}
    if "params" in shown:
        shown["params"] = {key: value for key, value in shown["params"].items() if key != "_meta"}
    if "result" in shown:
        shown["result"] = {key: value for key, value in shown["result"].items() if key not in UNUSED}
    text = json.dumps(shown)
    return text if len(text) <= 84 else text[:81] + "..."


class Watched(McpClient):
    """An McpClient that prints each message as it goes past."""

    def send(self, message):
        print("  ->", short(message))
        super().send(message)

    def reply_to(self, number):
        reply = super().reply_to(number)
        print("  <-", short(reply))
        return reply


def try_server(label, command, tool, arguments, cwd=None):
    print(label)
    with Watched(command, cwd=cwd, timeout=20) as server:
        print("  connected, era:", server.era)
        names = [item.name for item in server.tools()]
        print("  tools:", names)
        print("  answer:", server.call(tool, arguments))


try_server("New server, SDK v2", [sys.executable, "shifts_server.py"], "get_rota", {"staff_number": "1042"})
if len(sys.argv) > 1:
    try_server("Older server, SDK v1", [sys.argv[1], "older_server.py"], "stamps_left", {"stamps": 7}, cwd="older_server")
