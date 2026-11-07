"""The rota on SDK v2, with logging that goes to standard output. Say flushed or many."""
import sys

from mcp.server import MCPServer

LOG = sys.argv[1]
mcp = MCPServer("quillon-chatty")


@mcp.tool()
def get_rota() -> str:
    """Look up the next shift."""
    for number in range(20000 if LOG == "many" else 1):
        print("looking up the rota", number, flush=LOG == "flushed")
    return "Your next shift is Friday at 07:00."


if __name__ == "__main__":
    mcp.run()
