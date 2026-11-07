"""Read the saved runs from local_and_mcp.py: the totals, and every question whose score moved."""
from library import saved
from whitebox import load_report

reports = [load_report(saved(f"eval-{label}.json")) for label in ("local", "mcp", "local-again")]
print(f"{'Question':<24} {'local':>6} {'mcp':>6} {'again':>6}")
for rows in zip(*(report.rows for report in reports)):
    scores = [row.passed for row in rows]
    if len(set(scores)) > 1:
        print(f"{rows[0].name:<24} {scores[0]:>6} {scores[1]:>6} {scores[2]:>6}")
totals = [report.score()[0] for report in reports]
print(f"{'Total of 126':<24} {totals[0]:>6} {totals[1]:>6} {totals[2]:>6}")
