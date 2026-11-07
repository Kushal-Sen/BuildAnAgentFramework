"""A server that keeps state without a session: tools pass a handle. Say where baskets live: memory or file."""
import json
import sys
import uuid
from pathlib import Path
from typing import Annotated

from mcp.server import MCPServer
from pydantic import Field

SHARED = len(sys.argv) > 1 and sys.argv[1] == "file"
STORE = Path("baskets.json")
memory = {}
mcp = MCPServer("quillon-baskets")


def load():
    return json.loads(STORE.read_text()) if SHARED and STORE.exists() else memory


def save(baskets):
    if SHARED:
        STORE.write_text(json.dumps(baskets))


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


if __name__ == "__main__":
    mcp.run()
