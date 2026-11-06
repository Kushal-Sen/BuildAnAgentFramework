"""Kill a job, and print what its checkpoint holds, before anything restarts it."""
import shutil
import sys
from collections import Counter
from pathlib import Path

from crash_once import attempt
from refunds import Bank, one_line
from whitebox import load_messages

job, crash_after = sys.argv[1], int(sys.argv[2])
folder = Path("run")
shutil.rmtree(folder, ignore_errors=True)
folder.mkdir()
code, _ = attempt(job, crash_after, folder)
print(f"Exit code {code}. Bank:", *Bank(folder).payments())
print("The save holds:")
for message in (load_messages(folder / "state.json") or [])[-12:]:  # The last 12 at most: a bad run can save thousands.
    calls = Counter(call.name for call in message.tool_calls)
    asked = ", ".join(f"{count} {name}" for name, count in calls.items())
    print(f"  {message.role}:", f"asked for {asked}" if asked else one_line(message.content, 60))
