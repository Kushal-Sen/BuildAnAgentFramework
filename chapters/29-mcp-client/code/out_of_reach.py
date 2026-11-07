"""Ask something only the rota knows. The rota lives in another program, and this agent has no way to reach it."""
from library import all_documents, build_index
from staff_agent import QUESTION, ask, staff_agent
from whitebox import load_model, search_tool

index = build_index(all_documents(), 60)
tools = [search_tool(index)]
print("Tools:", [item.name for item in tools])
print("Asking:", QUESTION)
ask(staff_agent(load_model(), tools), QUESTION, "Friday at 07:00")
