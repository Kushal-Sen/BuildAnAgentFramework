"""The rota server written the older way, with the v1 SDK. It needs its own environment: pip install "mcp>=1.28,<2"."""
import sys

from mcp.server.fastmcp import FastMCP

LOG = sys.argv[1] if len(sys.argv) > 1 else "quiet"
mcp = FastMCP("quillon-rota-older")


@mcp.tool()
def get_rota(staff_number: str) -> str:
    """Look up someone's next shift."""
    if LOG == "print":
        print("looking up the rota")
    if LOG == "flushed":
        print("looking up the rota", flush=True)
    if LOG == "stderr":
        print("looking up the rota", file=sys.stderr)
    if LOG == "many":
        for number in range(20000):
            print("looking up the rota", number)
    return "Your next shift is Friday at 07:00."


if __name__ == "__main__":
    mcp.run()
