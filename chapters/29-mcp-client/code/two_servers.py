"""One agent, one local tool, and two servers from different generations. It needs the older environment's Python."""
import sys

from library import all_documents, build_index
from staff_agent import staff_agent, tools_called
from whitebox import McpClient, load_model, search_tool

QUESTIONS = [
    ("My staff number is 1042. When is my next shift?", "get_rota", "Friday"),
    ("A customer has 7 stamps. How many more do they need for a free drink?", "stamps_left", "3"),
    ("How much is the till float?", "search_handbook", "150"),
]
RUNS = 5

index = build_index(all_documents(), 60)
with (McpClient([sys.executable, "shifts_server.py"]) as rota,
      McpClient([sys.argv[1], "older_server.py"], cwd="older_server") as loyalty):
    print("Rota server:", rota.era, "| Loyalty server:", loyalty.era)
    tools = [search_tool(index), *rota.tools(), *loyalty.tools()]
    print("Tools:", [item.name for item in tools])
    agent = staff_agent(load_model(), tools)
    for question, wanted, says in QUESTIONS:
        results = [agent.run(question) for _ in range(RUNS)]
        called = sum(wanted in tools_called(result) for result in results)
        right = sum(says in result.answer for result in results)
        print(question)
        print(f"  called {wanted}: {called} of {RUNS}, says {says!r}: {right} of {RUNS}")
        print(f"  for example: {' '.join(results[0].answer.split())[:76]}")
