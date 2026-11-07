"""Eight handbook questions, ten runs each. What does one more tool do to the tool the agent already had?"""
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Annotated

from library import OPTIONS, Remember, all_documents, build_index
from questions import HANDBOOK, to_case
from staff_agent import STAFF_SYSTEM, tools_called
from whitebox import Agent, LoopGuard, McpClient, RescueToolCalls, Retry, Toolbox, load_model, search_tool, tool

RUNS = 10
NAMED_SYSTEM = STAFF_SYSTEM + " Use search_handbook for anything about how Quillon works, and get_rota for someone's next shift."
SEARCH_FIRST = STAFF_SYSTEM + " Always call search_handbook before you say you don't know."


@tool
def get_rota(staff_number: Annotated[str, "The staff number"]) -> str:
    """Look up someone's next shift."""
    return "Your next shift is Friday at 07:00."


def measure(label, system, tools):
    agent = Agent(Retry(RescueToolCalls(model)), Toolbox(tools), system=system, options=OPTIONS, hooks=[LoopGuard()])
    searched = right = 0
    answers = []
    for case in cases:
        for _ in range(RUNS):
            result = agent.run(case.question)
            passed = all(check.test(result) for check in case.checks)
            used = "search_handbook" in tools_called(result)
            searched += used
            right += passed
            answers.append({"case": case.name, "searched": used, "passed": passed, "answer": result.answer})
    missed = Counter(answer["case"].split(":")[1] for answer in answers if not answer["searched"])
    print(f"{label:<30} {searched:>2} of {len(answers)} {right:>4} of {len(answers)}  {dict(missed) or ''}", flush=True)
    return {"label": label, "searched": searched, "right": right, "runs": len(answers), "answers": answers}


model = load_model()
cases = [to_case(row) for row in HANDBOOK if row[1] == "direct"]
search = search_tool(Remember(build_index(all_documents(), 60)))
print(f"{'Tools':<30} {'Searched':<8} {'Right':<8} Runs with no search", flush=True)
with McpClient([sys.executable, "shifts_server.py"]) as server:
    rows = [
        measure("search_handbook alone", STAFF_SYSTEM, [search]),
        measure("plus get_rota, over MCP", STAFF_SYSTEM, [search, *server.tools()]),
        measure("plus get_rota, local", STAFF_SYSTEM, [search, get_rota]),
        measure("over MCP, prompt says when", NAMED_SYSTEM, [search, *server.tools()]),
        measure("over MCP, prompt says search", SEARCH_FIRST, [search, *server.tools()]),
    ]
Path("adding_a_tool.json").write_text(json.dumps(rows, indent=1))
