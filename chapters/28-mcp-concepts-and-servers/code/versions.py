"""The library's version and the protocol's version are different things. Give a v1 Python to compare."""
import json
import subprocess
import sys
import textwrap

from by_hand import ME, read, request, send, start, stop

SERVERS = {"2": "rota_server.py", "1": "older_rota.py"}


def run(python, code):
    done = subprocess.run([python, "-c", code], capture_output=True, text=True, timeout=30)
    return (done.stdout + done.stderr).strip().splitlines()[-1].split(" (/")[0]  # Leave out long paths.


def speaks(python, script):
    """Ask for a version that doesn't exist: the server answers with the newest handshake it knows."""
    server = start(script, python=python, timeout=20)
    send(server, request(1, "server/discover"))
    reply = json.loads(read(server))
    stop(server)
    stateless = reply.get("result", {}).get("supportedVersions", "none")
    server = start(script, python=python, timeout=20)
    send(server, request(1, "initialize", new=False, protocolVersion="1999-01-01", capabilities={}, clientInfo=ME))
    handshake = json.loads(read(server))["result"]["protocolVersion"]
    stop(server)
    return stateless, handshake


for python in [sys.executable, *sys.argv[1:]]:
    library = run(python, "from importlib.metadata import version; print(version('mcp'))")
    stateless, handshake = speaks(python, SERVERS[library[0]])
    print(f"Library: mcp {library}")
    print(f"  Protocol without a handshake: {stateless}")
    print(f"  Newest protocol with a handshake: {handshake}")
    for line in ("from mcp.server import MCPServer", "from mcp.server.fastmcp import FastMCP"):
        print(textwrap.fill(f"{line} -> {run(python, line + '; print("imported")')}", 88, initial_indent="  ",
                            subsequent_indent="    "))
