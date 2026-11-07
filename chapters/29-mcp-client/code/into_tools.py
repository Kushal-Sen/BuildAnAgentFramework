"""What a server says about a tool, and the Tool McpClient makes from it."""
import json
import sys
import textwrap

from whitebox import McpClient, Tool

with McpClient([sys.executable, "shifts_server.py"]) as server:
    item = server.result("tools/list")["tools"][0]
    print("From the server:")
    print(textwrap.indent(textwrap.fill(json.dumps(item), 84), "  "))
    rota = server.as_tool(item)
    print("As a Tool:")
    print("  is it a Tool?", isinstance(rota, Tool))
    print("  name:", rota.name)
    print("  description:", rota.description)
    print("  required:", rota.parameters["required"])
    print('Calling it like any Tool: rota(staff_number="1042")')
    print(" ", rota(staff_number="1042"))

with McpClient([sys.executable, "tests/fake_mcp_server.py", "new"]) as server:
    item = server.result("tools/list")["tools"][0]
    print("A server that leaves out required:")
    print("  from the server:", item["inputSchema"].get("required", "missing"))
    print("  on the Tool:", server.as_tool(item).parameters["required"])
