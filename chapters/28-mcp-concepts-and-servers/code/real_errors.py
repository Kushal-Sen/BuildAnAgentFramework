"""Send a real server things it can't do, each on a new connection, and print what comes back."""
import json
import textwrap

from by_hand import read, request, send, start, stop


def short(line):
    """The part of a reply worth reading."""
    reply = json.loads(line)
    if "error" in reply:
        return f"protocol error {reply['error']['code']}: {reply['error']['message']}"
    if "content" not in reply["result"]:
        return "ok"
    if reply["result"].get("isError"):
        return "tool error: " + reply["result"]["content"][0]["text"].splitlines()[0]
    return "ok"


def attempt(title, *messages):
    print(title)
    server = start("rota_server.py", timeout=20)
    for message in messages:
        send(server, message)
        print(textwrap.fill(short(read(server)), 88, initial_indent="  ", subsequent_indent="    "))
    stop(server)


if __name__ == "__main__":
    attempt("A method that doesn't exist", request(1, "tools/run"))
    attempt("A tool that doesn't exist", request(1, "tools/call", name="get_menu", arguments={}))
    attempt("A missing argument", request(1, "tools/call", name="get_rota", arguments={}))
    attempt("The tool raises ValueError", request(1, "tools/call", name="get_rota", arguments={"staff_number": "9"}))
    attempt("The tool raises ToolError", request(1, "tools/call", name="get_rota", arguments={"staff_number": "0"}))
