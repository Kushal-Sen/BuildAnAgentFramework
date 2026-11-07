"""The two ways to open a connection. Give the path of a Python with mcp v1 to try the older server as well."""
import json
import sys

from by_hand import ME, read, request, send, start, stop

CALL = {"name": "get_rota", "arguments": {"staff_number": "1042"}}
OLD = "2025-06-18"


def text(line):
    reply = json.loads(line)
    if "error" in reply:
        return f"refused: {reply['error']['code']} {reply['error']['message']}"
    return reply["result"]["content"][0]["text"]


def new_opening(server):
    print("  New opening: no handshake, and _meta on every request")
    send(server, request(1, "server/discover"))
    reply = json.loads(read(server))
    if "error" in reply:
        print(f"    server/discover refused: {reply['error']['code']} {reply['error']['message']}")
        return False
    print("    server/discover says:", reply["result"]["supportedVersions"])
    send(server, request(2, "tools/call", **CALL))
    print("    tools/call:", text(read(server)))
    return True


def old_opening(server):
    print("  Old opening: a handshake first, then plain requests")
    send(server, request(1, "initialize", new=False, protocolVersion=OLD, capabilities={}, clientInfo=ME))
    print("    initialize agreed:", json.loads(read(server))["result"]["protocolVersion"])
    send(server, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    print("    notifications/initialized: sent, and no reply comes")
    send(server, request(2, "tools/call", new=False, **CALL))
    print("    tools/call:", text(read(server)))


def both(title, *command, **options):
    print(title)
    server = start(*command, timeout=20, **options)
    if new_opening(server):
        stop(server)
        server = start(*command, timeout=20, **options)  # It worked, so use a new connection for the old way.
    old_opening(server)  # If discover was refused, this carries on down the same connection.
    stop(server)


both("Server on SDK v2", "rota_server.py")
if len(sys.argv) > 1:
    both("Server on SDK v1", "older_rota.py", python=sys.argv[1])
