"""What each setup cost, and how often the agent searched again. Reads the saved runs, so no model is needed."""
from library import load_runs
from questions import HANDBOOK, RECORDS

LABELS = ["titles60", "titles60-again", "titles120", "hybrid60", "agent60", "agent60-again", "agent-hybrid60",
          "agent-hybrid60-again"]

print(f"{'Setup':<22} {'Calls':>6} {'Tokens in':>10} {'Stopped':>8}   (calls and tokens per question)")
for label in LABELS:
    runs = load_runs(f"{label}-runs.json")
    calls = sum(run["steps"] for run in runs) / len(runs)
    tokens = sum(run["tokens_in"] for run in runs) / len(runs)
    stopped = sum(run["stopped"] for run in runs)
    print(f"{label:<22} {calls:>6.2f} {tokens:>10,.0f} {stopped:>8}")

kinds = {row[2]: row[1] for row in HANDBOOK + RECORDS}
agent_runs = load_runs("agent60-runs.json") + load_runs("agent60-again-runs.json")

print("\nagent60, both runs: how many searches did each run make?")
print(f"{'Kind':<9} {'Runs':>5} {'None':>5} {'One':>5} {'More':>5}")
for kind in ["direct", "gap", "code", "hop", "none", "records"]:
    counts = [len(run["searches"]) for run in agent_runs if kinds[run["question"]] == kind]
    print(f"{kind:<9} {len(counts):>5} {counts.count(0):>5} {counts.count(1):>5} {sum(c > 1 for c in counts):>5}")
