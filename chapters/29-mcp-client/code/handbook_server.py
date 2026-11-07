"""The handbook search as an MCP server: chapter 28's server, with the same tool name and description as chapter 23."""
from typing import Annotated

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
