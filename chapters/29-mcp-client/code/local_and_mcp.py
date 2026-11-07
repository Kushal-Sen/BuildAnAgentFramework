"""The same 42 questions, three runs each, with the search as a local tool and over MCP. Local runs twice, to show the noise."""
import sys

from library import OPTIONS, Keep, Remember, all_documents, build_agent, build_index
from questions import HANDBOOK, RECORDS, summary, to_cases
from whitebox import AGENT_SYSTEM, Agent, LoopGuard, McpClient, RescueToolCalls, Retry, Toolbox, load_model, run_eval

model = load_model()
cases = to_cases(HANDBOOK + RECORDS)
index = Remember(build_index(all_documents(), 60))


def measure(agent, label):
    kept = Keep(agent)
    report = run_eval(kept, cases, runs=3, label=label)
    report.save(f"eval-{label}.json")
    kept.save(f"eval-{label}-runs.json")
    print(summary(report), flush=True)


measure(build_agent(model, index), "local")
with McpClient([sys.executable, "handbook_server.py"], timeout=120) as server:
    agent = Agent(Retry(RescueToolCalls(model)), Toolbox(server.tools()), system=AGENT_SYSTEM, options=OPTIONS,
                  hooks=[LoopGuard()])
    print("era:", server.era, flush=True)
    measure(agent, "mcp")
measure(build_agent(model, index), "local-again")
