"""Crash a job many times, at several points, and count what the bank did. Saves crashes-JOB.json."""
import json
import sys
import tempfile
from pathlib import Path

from crash_once import attempt
from refunds import Bank, one_line

POINTS = (2, 3, 4, 5)  # Kill the job right after this many payments.
RUNS = 5  # Runs at each point, so 20 crashes for each job.


def crash_and_restart(job, crash_after):
    """One crash and one restart, with its own empty bank. Return what happened."""
    with tempfile.TemporaryDirectory() as folder:
        first, _ = attempt(job, crash_after, folder)
        second, printed = attempt(job, 0, folder)
        return {"crash_after": crash_after, "first": first, "second": second, "said": one_line(printed),
                "payments": Bank(folder).payments()[:100], "unpaid": Bank(folder).unpaid()}


if __name__ == "__main__":
    job = sys.argv[1]
    rows = []
    for crash_after in POINTS:
        for _ in range(RUNS):
            row = crash_and_restart(job, crash_after)
            rows.append(row)
            repeats = len(row["payments"]) - len(set(row["payments"]))
            print(f"after {crash_after}: {repeats} repeats, {len(row['unpaid'])} unpaid", flush=True)
            Path(f"crashes-{Path(job).stem}.json").write_text(json.dumps(rows, indent=1))  # After every crash, like the job.
