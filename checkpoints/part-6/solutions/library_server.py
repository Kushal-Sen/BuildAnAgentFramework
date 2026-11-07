"""Part 6 checkpoint: the Larkfield Library catalogue, as an MCP server."""
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

BOOKS = {"dune": "on the shelf", "emma": "on loan until 14 March", "beloved": "on the shelf"}

mcp = MCPServer("larkfield-catalogue")


@mcp.tool()
def book_status(title: str) -> str:
    """Say whether a book is on the shelf or on loan."""
    key = title.lower()
    if key not in BOOKS:
        raise ToolError(f"Larkfield doesn't have {title}")
    return BOOKS[key]


@mcp.tool()
def delete_catalogue() -> str:
    """Provided: a tool nobody should be able to call. Delete the whole catalogue."""
    return "Deleted."


if __name__ == "__main__":
    mcp.run()
