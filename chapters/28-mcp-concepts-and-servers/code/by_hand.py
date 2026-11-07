"""Start a server, send it one line of JSON, and read one line back. Plain Python, with no SDK."""
import json
import subprocess
import sys
import textwrap
import threading

KEY = "io.modelcontextprotocol/"
ME = {"name": "by-hand", "version": "1"}
META = {KEY + "protocolVersion": "2026-07-28", KEY + "clientCapabilities": {}, KEY + "clientInfo": ME}


def start(*command, python=sys.executable, timeout=60, stderr=subprocess.DEVNULL):
    """Run a server as its own program. If it goes quiet, the timer kills it, so we can't wait forever."""
    server = subprocess.Popen([python, *command], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=stderr, text=True)
    timer = threading.Timer(timeout, server.kill)
    timer.daemon = True
    timer.start()
    return server


def send(server, message):
    server.stdin.write(json.dumps(message) + "\n")
    server.stdin.flush()


def read(server):
    return server.stdout.readline()


def stop(server):
    """Closing its input is how a stdio server is told to finish. Returns anything it still had to say."""
    server.stdin.close()
    rest = server.stdout.read()
    server.wait(timeout=10)
    return rest


def request(number, method, new=True, **params):
    """One request as a dictionary. new=True adds the fields the 2026-07-28 protocol wants on every request."""
    if new:
        params["_meta"] = META
    return {"jsonrpc": "2.0", "id": number, "method": method, "params": params}


def show(label, text):
    print(f"{label}:")
    print(textwrap.indent(textwrap.fill(text.strip(), 88), "  "))


def main(*command):
    server = start(*command)
    message = request(1, "tools/list")
    show("Sent", json.dumps(message))
    send(server, message)
    show("Read", read(server))
    stop(server)


if __name__ == "__main__":
    main(*sys.argv[1:])
