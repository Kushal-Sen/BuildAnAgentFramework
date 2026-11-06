"""Run the job with no crash, several times, and show what each model reply asked for."""
import sys

from crash_once import attempt

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 5

for number in range(1, RUNS + 1):
    _, printed = attempt("job_replies.py", 0, ".")
    print(f"run {number}: {printed}", flush=True)
