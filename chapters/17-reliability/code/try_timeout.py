"""Provided: give a slow tool a time limit. usage: python3 try_timeout.py"""
import time
from typing import Annotated

from whitebox import ToolCall, Toolbox, tool, with_timeout


@tool
def slow_lookup(order: Annotated[str, "The order number, such as A17"]) -> str:
    """Look up an order. This one takes far too long."""
    time.sleep(3)
    print("slow_lookup finished, even though nobody is waiting")
    return "Delivered"


toolbox = Toolbox([with_timeout(slow_lookup, 1)])
started = time.monotonic()
print(toolbox.run(ToolCall("slow_lookup", {"order": "A17"})))
print(f"The agent got its answer after {time.monotonic() - started:.0f} second")
