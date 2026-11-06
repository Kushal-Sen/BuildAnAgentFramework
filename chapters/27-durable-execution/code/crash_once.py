"""Kill a job right after a payment, start it again, and read the bank."""
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

from refunds import Bank

LIMIT = 180  # Seconds. A run that takes longer is stopped, so a runaway reply can't hang this script.


def attempt(job, crash_after, folder):
    """Run the job as a separate process. Return its exit code and the last of what it printed."""
    command = [sys.executable, job, str(crash_after), str(folder)]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=LIMIT)
    except subprocess.TimeoutExpired:
        return None, f"Stopped after {LIMIT} seconds"
    return done.returncode, done.stdout.strip()[-200:]


def twice(bank):
    """The orders the bank paid more than once."""
    return [order for order, count in Counter(bank.payments()).items() if count > 1]


if __name__ == "__main__":
    job, crash_after = sys.argv[1], int(sys.argv[2])
    folder = Path("run")
    shutil.rmtree(folder, ignore_errors=True)  # Start with an empty bank.
    folder.mkdir()
    bank = Bank(folder)

    code, printed = attempt(job, crash_after, folder)
    print(f"First run: exit code {code}")
    print("Bank:", *bank.payments())
    code, printed = attempt(job, 0, folder)
    print(f"Second run: exit code {code}. It said: {printed}")
    print("Bank:", *bank.payments())
    print("Paid twice:", *twice(bank) or ["nobody"])
    print("Not paid:", *bank.unpaid() or ["nobody"])
