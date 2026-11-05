"""Provided: five tool calls, as a confused model might send them. You don't need to change this file."""
from sales_tools import toolbox
from whitebox import ToolCall

CALLS = [
    ToolCall("read_file", {"path": "sales/monday.txt"}),
    ToolCall("open_file", {"path": "sales/monday.txt"}),
    ToolCall("read_file", {}),
    ToolCall("read_file", {"path": "sales/monday.txt", "encoding": "utf-8"}),
    ToolCall("read_file", {"path": "sales/friday.txt"}),
]

for call in CALLS:
    print(f"{call.name}({call.arguments})")
    print(f"    -> {toolbox.run(call)!r}")
