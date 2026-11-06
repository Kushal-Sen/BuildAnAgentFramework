"""Read the crash tests: your file for a job if you've made one, and ours if not."""
import json
import sys
from collections import Counter
from pathlib import Path

JOBS = {"job_restart": "Start again", "job_saved": "Save before calls", "job_saved_tools": "Save after tools too",
        "job_once": "With once", "job_until_done": "With until_done"}


def load(job):
    mine = Path(f"crashes-{job}.json")
    return json.loads((mine if mine.exists() else Path("results") / mine.name).read_text())


def extra(row):
    return len(row["payments"]) - len(set(row["payments"]))


def table():
    print(f"{'Setup':<22}{'Crashes':>8}{'Repeats':>9}{'Unpaid':>8}{'Clean':>7}{'Hit limit':>11}")
    for job, label in JOBS.items():
        rows = load(job)
        crashed = [row for row in rows if row["first"] not in (0, None)]  # A few runs never reached their crash.
        repeats = sum(extra(row) for row in crashed)
        unpaid = sum(len(row["unpaid"]) for row in crashed)
        clean = sum(not extra(row) and not row["unpaid"] for row in crashed)
        limit = sum(row["first"] is None or row["second"] is None for row in rows)
        print(f"{label:<22}{len(crashed):>8}{repeats:>9}{unpaid:>8}{clean:>7}{limit:>11}")


def by_point(job):
    """For one job, count each way the bank ended up, at each crash point."""
    rows = load(job)
    for point in sorted({row["crash_after"] for row in rows}):
        crashed = [row for row in rows if row["crash_after"] == point and row["first"] not in (0, None)]
        shapes = Counter((extra(row), len(row["unpaid"])) for row in crashed)
        text = ", ".join(f"{count} with {repeats} repeats, {unpaid} unpaid" for (repeats, unpaid), count in sorted(shapes.items()))
        print(f"after {point}: {text}")


if len(sys.argv) > 1:
    by_point(sys.argv[1])
else:
    table()
