"""The same agent and question as out_of_reach.py, plus the tools of a server we don't own."""
import sys

from library import all_documents, build_index
from staff_agent import QUESTION, ask, staff_agent
from whitebox import McpClient, load_model, search_tool

index = build_index(all_documents(), 60)
with McpClient([sys.executable, "shifts_server.py"]) as server:
    tools = [search_tool(index), *server.tools()]
    print("Tools:", [item.name for item in tools])
    print("Asking:", QUESTION)
    ask(staff_agent(load_model(), tools), QUESTION, "Friday at 07:00")
