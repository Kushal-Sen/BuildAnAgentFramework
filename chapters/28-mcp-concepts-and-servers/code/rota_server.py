"""A small real server that doesn't need Ollama. Say how it should log: quiet, print, flushed, stderr or many."""
import sys
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

LOG = sys.argv[1] if len(sys.argv) > 1 else "quiet"
SHIFTS = {"1042": "Friday at 07:00", "1077": "Saturday at 12:00"}
mcp = MCPServer("quillon-rota")


@mcp.tool()
def get_rota(staff_number: Annotated[str, Field(description="The staff number")]) -> str:
    """Look up someone's next shift."""
    if LOG == "print":
        print("looking up the rota")
    if LOG == "flushed":
        print("looking up the rota", flush=True)
    if LOG == "many":
        for number in range(20000):
            print("looking up the rota", number)
    if LOG == "stderr":
        print("looking up the rota", file=sys.stderr)
    if staff_number == "0":
        raise ToolError("Staff numbers don't start at 0")
    if staff_number not in SHIFTS:
        raise ValueError(f"No staff number {staff_number}")
    return f"Your next shift is {SHIFTS[staff_number]}."


if __name__ == "__main__":
    mcp.run()
