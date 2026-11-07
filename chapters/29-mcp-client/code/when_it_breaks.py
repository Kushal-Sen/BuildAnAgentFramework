"""Break a real server four ways, and see what reaches your code and what reaches the model."""
import sys

from whitebox import McpClient, McpError, ToolCall, Toolbox


def attempt(label, action, *arguments):
    print(label)
    try:
        print("  returned:", action(*arguments))
    except McpError as error:
        print("  raised McpError:", error)


with McpClient([sys.executable, "shifts_server.py"], timeout=3) as server:
    attempt("1. The tool says no", server.call, "get_rota", {"staff_number": "5"})
    attempt("2. No tool by that name", server.call, "get_menu", {})
    attempt("3. No method by that name", server.result, "tools/cancel")
    attempt("4. The tool hangs, so the server goes silent", server.call, "get_rota", {"staff_number": "9999"})
    attempt("   The same connection, straight after", server.call, "get_rota", {"staff_number": "1042"})
    toolbox = Toolbox(server.tools())
    server.process.kill()
    server.process.wait(timeout=5)
    attempt("5. The server has stopped", server.tools)
    print("What a Toolbox hands the model when the server has stopped")
    print("  returned:", toolbox.run(ToolCall("get_rota", {"staff_number": "1042"})))
