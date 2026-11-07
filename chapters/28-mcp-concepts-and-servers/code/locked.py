"""search_handbook works here. Then a second program, in another folder, tries to reach it."""
import subprocess
import sys
import tempfile
import textwrap

from library import all_documents, build_index
from whitebox import search_tool

search_handbook = search_tool(build_index(all_documents(), 60))
print("Inside this program:")
print(textwrap.indent(textwrap.fill(search_handbook(query="carry over annual leave")[:170], 88), "  "))

with tempfile.TemporaryDirectory() as folder:
    done = subprocess.run([sys.executable, "-c", "from whitebox import search_tool"], cwd=folder,
                          capture_output=True, text=True, timeout=30)
print("From a program in another folder:")
print("  " + done.stderr.strip().splitlines()[-1])
