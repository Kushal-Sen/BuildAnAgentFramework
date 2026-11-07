"""Worked answers to the chapter 28 exercises."""
import json

KEY = "io.modelcontextprotocol/"
VERSION = "2026-07-28"
ME = {"name": "exercises", "version": "1"}


def request_line(number, method, params):
    """TODO 1: Return one JSON-RPC request as a string, ready to write to a server: the four fields jsonrpc
    ("2.0"), id, method and params, as JSON, on one line, ending in a newline.
    """
    return json.dumps({"jsonrpc": "2.0", "id": number, "method": method, "params": params}) + "\n"


def with_meta(params):
    """TODO 2: Return a new dictionary holding everything in params, plus the _meta the 2026-07-28 protocol
    wants on every request: KEY + "protocolVersion" (VERSION), KEY + "clientCapabilities" (an empty
    dictionary) and KEY + "clientInfo" (ME). Don't change params itself.
    """
    meta = {KEY + "protocolVersion": VERSION, KEY + "clientCapabilities": {}, KEY + "clientInfo": ME}
    return {**params, "_meta": meta}


def reply_text(line):
    """TODO 3: A reply can fail in two ways, and a caller shouldn't have to care which. Take one line from a
    server, and return a string. A protocol error has "error" with a "message": return "Error: " and that
    message. A tool error has a result with isError true: return "Error: " and the text. Otherwise return
    the text. The text is in result["content"], a list of parts: join the "text" of each with a newline.
    """
    reply = json.loads(line)
    if "error" in reply:
        return "Error: " + reply["error"]["message"]
    text = "\n".join(part["text"] for part in reply["result"]["content"])
    return "Error: " + text if reply["result"].get("isError") else text


def opening(reply):
    """TODO 4: reply is the dictionary a server sent back to server/discover. Return "new" if its result lists
    VERSION in supportedVersions. Return "old" for anything else, because an older server refuses
    server/discover, and any failed discover means try the handshake.
    """
    versions = reply.get("result", {}).get("supportedVersions", [])
    return "new" if VERSION in versions else "old"


def add_to_basket(store, handle, item):
    """TODO 5: The stateless way. store is a dictionary of handle to list of items, shared by every copy of a
    server. Add item to that basket and return the whole list. If the handle isn't in store, return
    "Error: no basket called HANDLE", with the real handle in place of HANDLE. Keep nothing anywhere else.
    """
    if handle not in store:
        return f"Error: no basket called {handle}"
    store[handle].append(item)
    return store[handle]
