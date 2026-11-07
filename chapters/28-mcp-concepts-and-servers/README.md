# Chapter 28: MCP concepts and servers

**Time:** about 2.5 hours, including 30 minutes on why MCP went stateless. **You'll build:** a real MCP server for
the Quillon handbook, and you'll talk to it by hand, one line of JSON at a time.

## Where we are

Part 5 ended with an agent that can survive a crash. Everything it can do still lives inside its own program.
`search_handbook` is a Python function in your folder, with your index, your imports and your Python. Nobody else's agent
can use it, and your agent can't use tools written by anybody else.

This chapter starts Part 6, which fixes that with the Model Context Protocol, or MCP. The one new idea is small: **a tool
can live in another program, and the two programs talk with one line of JSON each way.**

You'll see that by hand first, with no library, so nothing about it is magic. Then you'll write a real server with the
official SDK, break it on purpose, and find out why the protocol changed shape this year. You won't connect your agent yet.
That's the next chapter.

## Before you start

Activate the `.venv` you made in chapter 05, and work in `chapters/28-mcp-concepts-and-servers/code`. This chapter adds one
package, the official MCP library:

```bash
python3 -m pip install -r requirements.txt
```

[Start Ollama](../00-setup/README.md#step-4-start-ollama), because the handbook server builds its index when it starts.
Only `locked.py`, `quillon_server.py` and `ask_handbook.py` need it.

There's nothing new in `whitebox/` this chapter. These scripts sit beside it, and each section explains the one it uses:

- `plain_server.py` and `by_hand.py` are the by-hand pair. They use no MCP library at all.
- `quillon_server.py`, `rota_server.py` and `basket_server.py` are real servers. `rota_server.py` needs no Ollama, so it's
  the one we break.
- `older_rota.py` is the rota server written the older way. It needs the older library, so it needs its own environment.
  **That part is optional.** Every older-server result is printed in this lesson. To run it yourself:

```bash
python3 -m venv .venv-older
.venv-older/bin/python -m pip install "mcp>=1.28,<2"
```

Then pass `.venv-older/bin/python` to the scripts that show it below. Leave it off, and they test the new library only.

To check the framework itself, run this from `code`:

```bash
python3 -m pytest tests
```

You should see `87 passed`. These tests use a fake model, so they don't need Ollama.

## 1. Locked inside your Python

Here's the tool you've used since chapter 23, called the normal way. Then [code/locked.py](code/locked.py) starts a second
Python program in an empty folder, and that program tries to import it.

```text
$ python3 locked.py
Inside this program:
  [annual-leave.md] Annual leave  The leave year runs from 1 April to 31 March. You may
  carry over up to 5 unused days into the next leave year. Anything above that is lost
From a program in another folder:
  ModuleNotFoundError: No module named 'whitebox'
```

Inside the program, it works. One folder away, Python can't even find it. You could copy `whitebox/` across, but then you'd
also copy the handbook, the index and the Ollama setup, and you'd keep every copy up to date. If the other agent is written
in another language, you can't import it at all.

The problem isn't the search. It's that the only way in is a Python function call.

## 2. What MCP is

MCP is a shared way for a program that has tools to tell another program what they are, and to run them when asked. There are
three names to learn:

| Name | What it is | In this course |
|---|---|---|
| **Server** | A program that offers tools | `quillon_server.py` |
| **Client** | The code that connects to one server | `by_hand.py` now, `McpClient` in chapter 29 |
| **Host** | The application the user runs, which holds the clients and the model | Your agent |

A server can offer three kinds of thing. **Tools** are functions the model chooses to call. **Resources** are data the
application can read, such as a file. **Prompts** are ready-made templates a user can pick. Tools are the part an agent
needs, so they're all we'll use.

Messages are [JSON-RPC 2.0](https://www.jsonrpc.org/specification): a small standard where a request has an `id`, a `method`
and `params`, and the reply carries the same `id`. That `id` is how you match a reply to its request.

Messages also need a way to travel, called a **transport**. MCP has two:

- **stdio:** the client starts the server as its own program, and they talk through its standard input and output. One JSON
  message per line. This is the local case, and it's what this course teaches.
- **Streamable HTTP:** the server runs somewhere else, and messages go over HTTP. This is how remote servers work.

## 3. One line each way

Before any library, here's a whole server in plain Python, from [code/plain_server.py](code/plain_server.py):

```python
for line in sys.stdin:
    request = json.loads(line)
    if request["method"] == "tools/list":
        result = {"tools": TOOLS}
    else:
        result = {"content": [{"type": "text", "text": "Your next shift is Friday at 07:00."}]}
    print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)
```

It's a loop. Read a line, work out a reply, write a line. It isn't a complete MCP server, because it ignores most of the
rules, but it shows what one is: a program that reads lines and writes lines. Notice `flush=True`. Without it, Python may hold
the reply in a buffer, and the client would wait for ever. We'll come back to that in section 9.

Now the other side, from [code/by_hand.py](code/by_hand.py):

```python
def start(*command, python=sys.executable, timeout=60, stderr=subprocess.DEVNULL):
    """Run a server as its own program. If it goes quiet, the timer kills it, so we can't wait forever."""
    server = subprocess.Popen([python, *command], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=stderr, text=True)
    timer = threading.Timer(timeout, server.kill)
    timer.daemon = True
    timer.start()
```

`subprocess.Popen` starts a program and keeps going, where `subprocess.run` would wait for it to finish. `stdin=subprocess.PIPE`
and `stdout=subprocess.PIPE` connect its input and output to us. `readline` waits for ever if the server goes quiet, so a
`threading.Timer` kills the server after `timeout` seconds, and then `readline` returns an empty string.

```python
def send(server, message):
    server.stdin.write(json.dumps(message) + "\n")
    server.stdin.flush()


def read(server):
    return server.stdout.readline()
```

That's the whole trick: write a line, flush it, read a line. **Predict:** the message is `tools/list`. What comes back?

```bash
python3 by_hand.py plain_server.py
```

```text
$ python3 by_hand.py plain_server.py
Sent:
  {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {"_meta":
  {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
  "io.modelcontextprotocol/clientCapabilities": {}, "io.modelcontextprotocol/clientInfo":
  {"name": "by-hand", "version": "1"}}}}
Read:
  {"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "get_rota", "description":
  "Look up someone's next shift.", "inputSchema": {"type": "object", "properties":
  {"staff_number": {"type": "string"}}}}]}}
```

The reply has `"id": 1`, the same as the request, and it lists one tool: a name, a description, and a schema for its
arguments. That's nearly the same shape as the tool schemas your agent has sent to the model since chapter 11.

`_meta` is the part you haven't seen. Our plain server ignores it, but a real one won't. It carries three fields on every
request: which protocol version you're using, what your client can do, and who you are.

## 4. A real server

Writing that loop properly is tedious: every rule, every error, every schema. The official
[Python SDK](https://github.com/modelcontextprotocol/python-sdk) does it for you. Here's the handbook as a server, all of
[code/quillon_server.py](code/quillon_server.py):

```python
from library import all_documents, build_index
from mcp.server import MCPServer
from pydantic import Field
from whitebox import excerpts

index = build_index(all_documents(), 60)
mcp = MCPServer("quillon-handbook")


@mcp.tool()
def search_handbook(query: Annotated[str, Field(description="What to look up, in a few words")]) -> str:
    """Search the staff handbook. Search again with new words if the result isn't enough."""
    return excerpts(index.search(query, 3)) or "Nothing found."


if __name__ == "__main__":
    mcp.run()
```

- `MCPServer("quillon-handbook")` makes the server and names it.
- `@mcp.tool()` turns a normal function into an MCP tool. Its name becomes the tool's name, and its docstring becomes the
  description, which is the same text as chapter 23.
- `Annotated[str, Field(description=...)]` describes the argument. The SDK uses `Field`, from a library called pydantic,
  where our own `@tool` took a plain string.
- `mcp.run()` starts the read-a-line loop on stdio, and doesn't return until the client closes the connection.

There's no `async` here, and there won't be in this course. The SDK uses it inside, and your tool stays a normal function.

**Predict:** run the same `by_hand.py`, with no changes, against this server. Does it work?

```bash
python3 by_hand.py quillon_server.py
```

```text
$ python3 by_hand.py quillon_server.py
Sent:
  {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {"_meta":
  {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
  "io.modelcontextprotocol/clientCapabilities": {}, "io.modelcontextprotocol/clientInfo":
  {"name": "by-hand", "version": "1"}}}}
Read:
  {"jsonrpc":"2.0","id":1,"result":{"cacheScope":"private","resultType":"complete","tools"
  :[{"description":"Search the staff handbook. Search again with new words if the result
  isn't enough.","inputSchema":{"type":"object","properties":{"query":{"description":"What
  to look up, in a few words","title":"Query","type":"string"}},"required":["query"],"titl
  e":"search_handbookArguments"},"name":"search_handbook","outputSchema":{"properties":{"r
  esult":{"title":"Result","type":"string"}},"required":["result"],"title":"search_handboo
  kOutput","type":"object"}}],"ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"na
  me":"quillon-handbook","version":""}}}}
```

The client didn't change at all, and that's the point of a protocol. The SDK built the schema from your function, including
`"required":["query"]`. It also added fields our plain server didn't have, such as `resultType`, `ttlMs` and `cacheScope`.
We won't need those. `tools` is what matters.

Now close the loop from section 1. [code/ask_handbook.py](code/ask_handbook.py) calls the tool with `tools/call`, and imports
only the standard library and `by_hand.py`:

```bash
python3 ask_handbook.py "carry over annual leave"
```

```text
$ python3 ask_handbook.py "carry over annual leave"
[annual-leave.md] Annual leave  The leave year runs from 1 April to 31 March. You may
carry over up to 5 unused days into the next leave year. Anything above that is lost
whitebox imported in this program: False
Seconds, with the server building its index: 7.5
```

It's the same text `locked.py` printed, from a program that never imported `whitebox`. The text came back the same in five
runs out of five. Our print cuts it at 170 characters, as `locked.py` does.

The time is nearly all the server building its index, which it does each time it starts. A client starts a server once and
keeps it, so that's a cost per connection, not per call.

## 5. Real errors

Now break things. [code/real_errors.py](code/real_errors.py) sends `rota_server.py` five bad requests, each on a new
connection. `rota_server.py` has a `get_rota` tool, and it needs no Ollama, so this is quick. **Predict:** which of these does
the model get to read?

```text
$ python3 real_errors.py
A method that doesn't exist
  protocol error -32601: Method not found
A tool that doesn't exist
  tool error: Unknown tool: get_menu
A missing argument
  tool error: Error executing tool get_rota: 1 validation error for get_rotaArguments
The tool raises ValueError
  tool error: Error executing tool get_rota
The tool raises ToolError
  tool error: Error executing tool get_rota: Staff numbers don't start at 0
```

There are two different kinds of failure here, and they arrive in different places:

- A **protocol error** comes back under `"error"`, with a code. Your request was wrong, and no tool ran. `-32601` means there's
  no such method.
- A **tool error** comes back as a normal `"result"` with `"isError": true`, and the message is in the text. It's written for
  the model to read, so it can try something else.

Look at the two raises. The tool raised `ValueError("No staff number 9")`, and that message never left the server. The client
got only `Error executing tool get_rota`, which tells the model nothing. `ToolError` is the one exception whose message the
SDK passes on. So when you want the model to read why, raise `ToolError` or return the text. Returning `"Error: ..."` is what
your tools have done since chapter 14, and `basket_server.py` does it in section 8.

Now the error worth remembering. [code/era_lock.py](code/era_lock.py) tries three orders of requests.
**Predict:** the first request in the first case is wrong. If the next one is right, does it work?

```text
$ python3 era_lock.py
Forget _meta, then send a good request
  protocol error -32602: Invalid request parameters
  protocol error -32600: this connection serves the handshake protocol era; requests
    carrying the 2026-07-28 envelope are not accepted on it
A harmless ping with no _meta, then a good request
  ok
  protocol error -32600: this connection serves the handshake protocol era; requests
    carrying the 2026-07-28 envelope are not accepted on it
A good request, then forget _meta
  ok
  protocol error -32602: params._meta must be an object carrying the required
    'io.modelcontextprotocol/protocolVersion' and
    'io.modelcontextprotocol/clientCapabilities' envelope keys
```

It doesn't. **The first request sets which protocol the connection speaks.** A first request with no `_meta` tells the server
this is an older client, so the connection locks into the old protocol, and a perfect request is refused after that. Even a
harmless `ping` does it, and that `ping` got an ordinary success reply, so nothing warned you. "Handshake protocol era" is the
server's name for the old protocol.

The third case is the reverse: a connection that began with the new protocol wants `_meta` on every request.

So if you see this error, don't look at the request it refused. Look at the first one you sent. The fix is a new connection.

## 6. Two ways to open

That lock exists because there are two protocols. A server on the older library speaks only the older one, so you need to know both.

[code/both_openings.py](code/both_openings.py) tries each opening on a v2 server. On the older server, it tries the new
opening, and carries on down the same connection after the refusal. We ran it with the older environment:

```bash
python3 both_openings.py .venv-older/bin/python
```

```text
$ python3 both_openings.py .venv-older/bin/python
Server on SDK v2
  New opening: no handshake, and _meta on every request
    server/discover says: ['2026-07-28']
    tools/call: Your next shift is Friday at 07:00.
  Old opening: a handshake first, then plain requests
    initialize agreed: 2025-06-18
    notifications/initialized: sent, and no reply comes
    tools/call: Your next shift is Friday at 07:00.
Server on SDK v1
  New opening: no handshake, and _meta on every request
    server/discover refused: -32602 Invalid request parameters
  Old opening: a handshake first, then plain requests
    initialize agreed: 2025-06-18
    notifications/initialized: sent, and no reply comes
    tools/call: Your next shift is Friday at 07:00.
```

**The new opening** has no opening. Every request carries `_meta`, so you can send `tools/call` first. `server/discover` is
optional. You'd use it to ask what a server supports.

**The old opening** is a handshake. You send `initialize` and get a reply, then send `notifications/initialized`, which has no
`id` and gets no reply. After that come plain requests with no `_meta`.

The v2 server answered both. The older server refused `server/discover` with `-32602 Invalid request parameters`, the same
error as skipping the handshake. The connection survived that, and the handshake worked straight after it. So a client can
try the new way, and if the attempt fails in any way, try the handshake. We've only tested that on Python SDK servers.

After opening, `tools/list` and `tools/call` are the same on both, apart from `_meta`. Chapter 29 builds that choice into a
client.

## 7. The protocol's version and the library's version

Two different things have versions here, and they're easy to blur.

- `2026-07-28` is a **protocol** version: the rules for the messages. It's a date. Any language can follow it.
- `2.3.0` is a **library** version: one Python package, `mcp`, which you install with pip. It's a number.

A library can speak several protocols. [code/versions.py](code/versions.py) asks each library what it speaks, and tries each
library's import:

```bash
python3 versions.py .venv-older/bin/python
```

```text
$ python3 versions.py .venv-older/bin/python
Library: mcp 2.3.0
  Protocol without a handshake: ['2026-07-28']
  Newest protocol with a handshake: 2025-11-25
  from mcp.server import MCPServer -> imported
  from mcp.server.fastmcp import FastMCP -> ModuleNotFoundError: No module named
    'mcp.server.fastmcp'. This is mcp 2.x, where FastMCP was renamed to MCPServer (from
    mcp.server.mcpserver import MCPServer) and other APIs changed; see the migration
    guide at https://py.sdk.modelcontextprotocol.io/v2/migration/#fastmcp-renamed-to-
    mcpserver or pin 'mcp<2' to keep running v1 code.. Did you mean: 'mcp.server.auth'?
Library: mcp 1.30.0
  Protocol without a handshake: none
  Newest protocol with a handshake: 2025-11-25
  from mcp.server import MCPServer -> ImportError: cannot import name 'MCPServer' from
    'mcp.server'
  from mcp.server.fastmcp import FastMCP -> imported
```

So "v2" means the Python library, and "stateless" means the protocol. Library 2.3.0 speaks the stateless protocol and the
handshake one. Library 1.30.0 speaks only the handshake one. Both agree on the newest handshake version, `2025-11-25`. To find
that, the script asks for a version that doesn't exist, and the server answers with its newest. `both_openings.py` asks for
`2025-06-18`, an older handshake version, and both servers accept it.

The import lines matter when you search online. Library v2 renamed `FastMCP` to `MCPServer`, and tutorials from before v2 show
`FastMCP`. If you copy one, you'll get the first error above, and its message tells you what to do. The second import has no
`Did you mean`, so if you see `cannot import name 'MCPServer'`, you've got the older library.

## 8. Why MCP went stateless

Why change a protocol that worked? The official post says only "better reliability and scalability". The clearest reasons
are in [Google's write-up](https://developers.googleblog.com/scaling-ai-agent-infrastructure-with-the-mcp-stateless-updates/),
and they're all about running a remote server as several copies:

- A load balancer doesn't know which copy holds a session.
- Sticky routing, which sends each client back to the same copy, spreads traffic unevenly.
- A restart wipes any session held in memory.
- So teams had to add a shared store, such as Redis.

You can see all four without any networking. [code/two_copies.py](code/two_copies.py) is pretend: no MCP, only two `Copy`
objects and a balancer that takes turns.

```python
    def remembered(self, session):
        """The older way: the request names a session, and this copy must remember it."""
        if session not in self.sessions:
            return f"{self.name}: unknown session"
        self.served += 1
        return f"{self.name}: ok"
```

`remembered` is the older way. The request names a session, and this copy has to know it. `self_contained`, beside it in the
file, only checks what the request itself carries. **Predict:** the handshake lands on copy A. What happens to the next four
requests?

```text
$ python3 two_copies.py
1. Session remembered by copy A, balancer takes turns
  B: unknown session | A: ok | B: unknown session | A: ok
2. Self-contained requests, balancer takes turns
  B: ok | A: ok | B: ok | A: ok
3. Sticky routing: each client always goes to the copy that holds its session
  100 requests: A served 95, B served 5
  Self-contained, taking turns: A served 50, B served 50
4. Restart copy A: memory is wiped
  before: A: ok
  after:  A: unknown session
  self-contained after: A: ok
5. A shared store, as teams built with Redis: it works, and it's one more service to run
  A: ok | B: ok
```

- **Case 1:** every request that lands on B fails, because the session lives in A's memory.
- **Case 2:** the same balancer, and everything works, because no copy needs to remember anything.
- **Case 3:** sticky routing fixes the failures, but one busy client pins 95 of 100 requests to one copy. The traffic is
  made up to show the shape.
- **Case 4:** a restart loses the session. A self-contained request doesn't care.
- **Case 5:** a shared store works, and it's one more service to run and pay for.

That's why `_meta` is on every request. It's what makes a request self-contained.

### Stateless doesn't mean your app has no state

A coffee order needs a basket, and a basket has to live somewhere between calls. The protocol stopped holding state, so your
application holds it, and names it with a **handle**: an ordinary string that one tool returns and later tools take as an
argument. From [code/basket_server.py](code/basket_server.py):

```python
@mcp.tool()
def new_basket() -> str:
    """Start an empty basket, and return its handle."""
    baskets = load()
    handle = "basket-" + uuid.uuid4().hex[:6]
    baskets[handle] = []
    save(baskets)
    return handle


@mcp.tool()
def add_to_basket(basket: Annotated[str, Field(description="The handle from new_basket")],
                  item: Annotated[str, Field(description="What to add")]) -> str:
    """Add one item to a basket, and say what's in it."""
    baskets = load()
    if basket not in baskets:
        return f"Error: no basket called {basket}"
    baskets[basket].append(item)
    save(baskets)
    return ", ".join(baskets[basket])
```

`basket` is a normal argument, with a normal description. The model can pass it along like any other value.
[code/handles.py](code/handles.py) starts **two real copies** of this server and takes turns between them. It runs once with
baskets in each copy's memory, and once with baskets in a file both can read. **Predict:** does the handle alone save the first
run?

```text
$ python3 handles.py
Baskets kept in memory
  copy A: new_basket -> basket-7dc3e0
  copy B: add flat white -> Error: no basket called basket-7dc3e0
  copy A: add oat milk -> oat milk
  copy B: add almond croissant -> Error: no basket called basket-7dc3e0
Baskets kept in file
  copy A: new_basket -> basket-376143
  copy B: add flat white -> flat white
  copy A: add oat milk -> flat white, oat milk
  copy B: add almond croissant -> flat white, oat milk, almond croissant
```

No. With baskets in memory, copy B has never heard of the handle, and copy A's basket misses the items B was sent. It's the
session problem again, in your own code. With baskets in a file, either copy can serve any call, and neither one remembers
anything between calls. A handle only helps if it points at something every copy can reach. A file is fine for a demo. Two
copies writing at once could overwrite each other, so real servers use a database.

### How much this changes for you

Be plain about this: **on local stdio, very little.** One client starts one server, so no balancer can send you to the wrong
copy, and a restart ends the connection anyway. Remote servers gain the most. Learn the new shape because that's where the
protocol is going, and learn the handshake because a server on the older library speaks nothing else. The deprecation policy gives older features
at least twelve months.

## 9. A stray print

On stdio, a server's standard output *is* the protocol's pipe. `print` writes to standard output. So what does a `print`
inside a tool do? You may have read that one `print` always breaks a server. We tested it.

[code/stray_print.py](code/stray_print.py) makes one call to a tool that logs in five different ways, five runs each, on both
libraries. `print` is a plain print. `flushed` adds `flush=True`. `stderr` uses `file=sys.stderr`. `many` prints 20,000 lines.
The numbers count lines of logging, and a range would show if the runs differed. This takes about two minutes with the older
library, because each failed run waits for its 20-second timer.

```bash
python3 stray_print.py .venv-older/bin/python
```

```text
$ python3 stray_print.py .venv-older/bin/python
SDK v2
  log      answered  before reply  after reply  stderr
  quiet    5 of 5    0             0            0
  print    5 of 5    0             1            0
  flushed  5 of 5    0             0            1
  stderr   5 of 5    0             0            1
  many     5 of 5    0             648          19353
SDK v1
  log      answered  before reply  after reply  stderr
  quiet    5 of 5    0             0            0
  print    5 of 5    0             0            0
  flushed  5 of 5    1             0            0
  stderr   5 of 5    0             0            1
  many     0 of 5    19984         0            0
  The reply arrived as: looking up the rota 19983{"jsonrpc":"2.0","id":2,"result":{"
```

So it depends on the library, and on how much you print.

- **A plain `print` disturbed nothing here.** When standard output is a pipe, Python holds text in a buffer. On v2, the line
  reached the pipe when the server exited, after the reply. On v1, it never reached the pipe at all.
- **`flush=True` differs.** On v1, the line went into the pipe before the reply, so a client that parses every line as
  JSON would crash on it. The call still got its answer here, because our script skips lines that aren't the reply. On v2,
  the line went to stderr, because v2 points standard output at stderr while it serves, and puts it back at exit.
- **`many` shows the real danger.** Enough text overflows the buffer. On v2, 19,353 lines went safely to stderr, and the rest
  reached the pipe at exit. On v1, **0 of 5 calls got an answer.** The overflow stopped halfway through a line, and the reply
  was written straight onto the end of it, as the last line of the output shows. That line isn't valid JSON, so no client can
  read it.

One plain `print` doesn't always break a server, and you shouldn't rely on that. Your server might run on another library or
another language, and the result changes with how much you print. The `stderr` row is the same on both, so **log to stderr**.
In chapter 29, `McpClient` sets aside lines that aren't JSON, so a noisy server doesn't crash your agent. Nothing can rescue a
reply that's been damaged, though.

## 10. What production uses instead

Your by-hand client is for learning. Production code would use the official SDK's client, which handles every rule of the
protocol, and it's async. We're not using it, because this course doesn't teach `async`, and because writing a small client
yourself shows what's really on the wire. Remote servers would also use Streamable HTTP, with real authentication.

## What this does and doesn't show

- We ran one Mac with Python 3.15, `mcp` 2.3.0 and `mcp` 1.30.0. Other libraries and other languages may differ, and the
  print results in particular depend on the library.
- There's no model in this chapter, and so no model behaviour to measure. The only model used is the embedding one, inside
  the handbook search.
- The two-copies demo is pretend, and its traffic is made up. It shows why sessions and balancers clash, not how much it costs.
  `handles.py` runs real servers, but through a loop in our script, not a real balancer.
- Falling back from a failed `server/discover` was tested on Python SDK servers only.
- The reasons for going stateless come from Google's write-up. We haven't measured a remote server.

## Reading errors

| What you see | What it means | What to do |
|---|---|---|
| `-32601 Method not found` | That method doesn't exist | Check the spelling: it's `tools/call` |
| `-32602 Invalid request parameters` | Often a request with no `_meta` and no handshake | Add `_meta`, or do the handshake, on a new connection |
| `this connection serves the handshake protocol era` | The first request locked the connection | Start a new connection, and send `_meta` from the first request |
| `params._meta must be an object carrying...` | The connection is on the new protocol, and this request has no `_meta` | Put `_meta` on every request |
| `Unknown tool: ...` with `isError` | No tool has that name | Call `tools/list` and check |
| `Error executing tool NAME`, and nothing else | The tool raised something other than `ToolError` | Raise `ToolError`, or return the text, and read the server's stderr |
| `No module named 'mcp.server.fastmcp'` | A v1 tutorial on library v2 | `from mcp.server import MCPServer` |
| `cannot import name 'MCPServer'` | Library v1 | `python3 -m pip install -r requirements.txt` |
| Your client hangs, then gets an empty string | The server died, or never replied, and the timer killed it | Run the server alone and read its error |
| `json.JSONDecodeError` in your client | Something other than JSON reached the pipe | Find the `print`, and send it to stderr |

## Exercises

Open `exercises.py` in `chapters/28-mcp-concepts-and-servers`. Each TODO is one small piece of a client or a server.

1. `request_line`: build one request, ready to write to a server. The check sends it to `plain_server.py`.
2. `with_meta`: add the three fields the new protocol wants, without changing what you were given.
3. `reply_text`: turn a reply line into text, for both kinds of failure.
4. `opening`: read a `server/discover` reply, and choose `"new"` or `"old"`.
5. `add_to_basket`: the handle idea, with all the state in the store you're given.

Run this from that folder. These checks need neither Ollama nor `mcp`:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in [solutions/exercises.py](solutions/exercises.py).

**Exercise 6, optional: your own tool.** Add a second tool to `quillon_server.py`, such as one that lists the handbook's files.
Change nothing else, and run `by_hand.py` on it. Does it appear in `tools/list`? What did the SDK do with your docstring?
There's no worked answer, because it's your tool.

## Common mistakes

- **Forgetting `flush`.** A written line that's still in a buffer never arrives, and both programs wait.
- **Reading with no timeout.** `readline` will wait for ever on a quiet server.
- **Looking at the wrong request.** The handshake-era error is caused by your first request, not the one it refused.
- **Trusting `ping` as a test.** It succeeds, and it locks the connection if it has no `_meta`.
- **Raising a plain exception for the model to read.** Its message never leaves the server.
- **Mixing up `2026-07-28` and `2.3.0`.** One's the protocol, and the other's the library.
- **Copying `FastMCP` from a tutorial.** That's the v1 name.
- **Logging with `print`.** Log to stderr.
- **Keeping a handle's data in one copy's memory.** The handle has to point at something every copy can reach.
- **Reading "stateless" as "no state".** The protocol stopped holding it. Your application still can.

## Recap

- `search_handbook` was locked inside your Python: a program one folder away got `ModuleNotFoundError`.
- MCP puts a tool in its own program. On stdio, that's one line of JSON each way, matched by `id`.
- A server is a loop that reads and writes lines, and `by_hand.py` talked to a plain one and a real one without changing.
- `MCPServer` and `@mcp.tool()` build the name, description and schema from a normal function.
- A protocol error means no tool ran. A tool error is a normal result, with `isError` set and text for the model.
- The first request sets the protocol for that connection, and a wrong first request locks it into the old one.
- The new opening needs no handshake, because every request carries `_meta`. The old opening is `initialize`, then
  `notifications/initialized`. A v2 server answers both.
- `2026-07-28` is a protocol, and `2.3.0` is a library that speaks it. `FastMCP` became `MCPServer`.
- Sessions in memory clash with load balancers, sticky routing and restarts. Self-contained requests work on any copy.
- A handle carries your state as an ordinary argument, if what it points at is shared. On local stdio, little changes.
- A plain `print` disturbed nothing in our runs, and 20,000 lines damaged every reply on v1. Log to stderr.

The tool lives in its own program now. The rest is agreeing how to talk.

## Where this comes from

The protocol is defined in the [MCP specification](https://modelcontextprotocol.io/specification), and the server code uses
the [official Python SDK](https://github.com/modelcontextprotocol/python-sdk). The
[official post on the 2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) gives the twelve-month
deprecation window, and says stateless was wanted for "better reliability and scalability". The four reasons in section 8 come
from [Scaling AI agent infrastructure with the MCP stateless updates](https://developers.googleblog.com/scaling-ai-agent-infrastructure-with-the-mcp-stateless-updates/),
by Kurtis Van Gent and Alan Blount of Google Cloud. Messages follow [JSON-RPC 2.0](https://www.jsonrpc.org/specification).

**Next:** chapter 29 builds `McpClient`, so your agent can use tools it doesn't own, on new and older servers.
