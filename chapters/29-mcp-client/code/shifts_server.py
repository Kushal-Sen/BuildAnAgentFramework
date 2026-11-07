"""The rota, as a real MCP server. Someone else's program: your agent doesn't own this code, and it needs no Ollama."""
import time
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

SHIFTS = {"1042": "Friday at 07:00", "1077": "Saturday at 12:00"}
mcp = MCPServer("quillon-rota")


@mcp.tool()
def get_rota(staff_number: Annotated[str, Field(description="The staff number")]) -> str:
    """Look up someone's next shift."""
    if staff_number == "9999":
        time.sleep(3600)  # A tool that hangs, so we can see what a silent server does to a client.
    if staff_number not in SHIFTS:
        raise ToolError(f"No staff number {staff_number}")
    return f"Your next shift is {SHIFTS[staff_number]}."


if __name__ == "__main__":
    mcp.run()
