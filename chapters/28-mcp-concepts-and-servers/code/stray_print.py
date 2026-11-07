"""What does a print inside a tool do? Five runs of each way of logging. Give a v1 Python to test that SDK too."""
import json
import sys
import tempfile

from by_hand import ME, read, request, send, start, stop

CALL = {"name": "get_rota", "arguments": {"staff_number": "1042"}}
RUNS = 5


def reply_in(line):
    """True if this line is the reply we're waiting for."""
    try:
        return json.loads(line).get("id") == 2
    except ValueError:
        return False


def one_run(script, kind, python):
    """Make one call, count stdout lines before and after the reply, and count lines on stderr."""
    with tempfile.TemporaryFile("w+") as log:
        server = start(script, kind, python=python, timeout=20, stderr=log)
        send(server, request(1, "initialize", new=False, protocolVersion="2025-06-18", capabilities={}, clientInfo=ME))
        read(server)
        send(server, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        send(server, request(2, "tools/call", new=False, **CALL))
        before = 0
        damaged = ""
        line = read(server)
        while line and not reply_in(line):
            before += 1
            damaged = line if "jsonrpc" in line else damaged
            line = read(server)
        after = len(stop(server).splitlines()) if line else 0
        log.seek(0)
        logged = sum("looking up" in text for text in log)
    return bool(line), before, after, logged, damaged[:60].strip()


def spread(numbers):
    return str(min(numbers)) if min(numbers) == max(numbers) else f"{min(numbers)}-{max(numbers)}"


def test(title, script, python):
    print(title)
    print(f"  {'log':8} {'answered':9} {'before reply':13} {'after reply':12} stderr")
    for kind in ("quiet", "print", "flushed", "stderr", "many"):
        runs = [one_run(script, kind, python) for _ in range(RUNS)]
        answered, before, after, logged, damaged = zip(*runs)
        print(f"  {kind:8} {sum(answered)} of {RUNS}    {spread(before):13} {spread(after):12} {spread(logged)}")
        if damaged[0]:
            print(f"  The reply arrived as: {damaged[0]}")


test("SDK v2", "rota_server.py", sys.executable)
if len(sys.argv) > 1:
    test("SDK v1", "older_rota.py", sys.argv[1])
