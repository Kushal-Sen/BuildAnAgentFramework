"""Use search_handbook without importing any of it. Only the standard library and by_hand.py run in this program."""
import json
import sys
import textwrap
import time

from by_hand import read, request, send, start, stop

began = time.time()
server = start("quillon_server.py")
send(server, request(1, "tools/call", name="search_handbook", arguments={"query": sys.argv[1]}))
reply = json.loads(read(server))
stop(server)
print(textwrap.fill(reply["result"]["content"][0]["text"][:170], 88))
print(f"whitebox imported in this program: {'whitebox' in sys.modules}")
print(f"Seconds, with the server building its index: {time.time() - began:.1f}")
