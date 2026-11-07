"""The same chatty server on SDK v1. It needs the older environment."""
import sys

from mcp.server.fastmcp import FastMCP

LOG = sys.argv[1]
mcp = FastMCP("quillon-chatty-older")


@mcp.tool()
def get_rota() -> str:
    """Look up the next shift."""
    for number in range(20000 if LOG == "many" else 1):
        print("looking up the rota", number, flush=LOG == "flushed")
    return "Your next shift is Friday at 07:00."


if __name__ == "__main__":
    mcp.run()
