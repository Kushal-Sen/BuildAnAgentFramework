"""Print the control test, then every answer it marked wrong."""
from library import load_runs

runs = load_runs("plan-control.json")
setups = list(dict.fromkeys(run["setup"] for run in runs))

print(f"{'Setup':<14}{'Direct':>8}{'Unanswerable':>14}{'Total':>8}{'Calls':>7}")
for setup in setups:
    rows = [run for run in runs if run["setup"] == setup]
    direct = [row for row in rows if row["kind"] == "direct"]
    none = [row for row in rows if row["kind"] == "none"]
    right = sum(row["good"] for row in rows)
    calls = sum(row["calls"] for row in rows) / len(rows)
    print(f"{setup:<14}{sum(r['good'] for r in direct):>5}/{len(direct)}{sum(r['good'] for r in none):>11}/{len(none)}"
          f"{right:>5}/{len(rows)}{calls:>7.1f}")

print()
for run in runs:
    if not run["good"]:
        print(f"{run['setup']}, {run['name']}: {' '.join(run['answer'].split())[:120]}")
