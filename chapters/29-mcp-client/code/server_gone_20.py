"""server_gone.py with 20 runs and whole answers, because 80 characters can't show whether the model made up a shift."""
import sys

from library import all_documents, build_index
from staff_agent import QUESTION, staff_agent, tools_called
from whitebox import McpClient, load_model, search_tool

index = build_index(all_documents(), 60)
with McpClient([sys.executable, "shifts_server.py"]) as server:
    tools = [search_tool(index), *server.tools()]
    server.process.kill()
    server.process.wait(timeout=5)
    agent = staff_agent(load_model(), tools)
    for run in range(1, 21):
        result = agent.run(QUESTION)
        print(f"{run}. called {tools_called(result)}")
        print(f"   {' '.join(result.answer.split())}")
