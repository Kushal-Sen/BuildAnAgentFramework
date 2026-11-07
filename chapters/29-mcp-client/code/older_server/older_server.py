"""An MCP server written the older way, with the v1 Python SDK. It needs its own environment.

python3 -m venv .venv-older
.venv-older/bin/python -m pip install -r requirements.txt
"""
from mcp.server.fastmcp import FastMCP

STAMPS_FOR_A_FREE_DRINK = 10

mcp = FastMCP("quillon-loyalty")


@mcp.tool()
def stamps_left(stamps: int) -> int:
    """Say how many more stamps a customer needs for a free drink."""
    return max(STAMPS_FOR_A_FREE_DRINK - stamps, 0)


if __name__ == "__main__":
    mcp.run()
