"""Connect, then kill the server, then ask. Does the agent crash, and what does the model say?"""
import sys

from library import all_documents, build_index
from staff_agent import QUESTION, ask, staff_agent
from whitebox import McpClient, load_model, search_tool

index = build_index(all_documents(), 60)
with McpClient([sys.executable, "shifts_server.py"]) as server:
    tools = [search_tool(index), *server.tools()]
    server.process.kill()
    server.process.wait(timeout=5)
    print("The server is stopped. Tools the agent still thinks it has:", [item.name for item in tools])
    print("Asking:", QUESTION)
    ask(staff_agent(load_model(), tools), QUESTION, "Friday at 07:00")
