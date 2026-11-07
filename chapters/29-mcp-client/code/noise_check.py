"""What McpClient.noise catches. Five runs of each server. Pass the older environment's Python to try SDK v1 as well."""
import sys

from whitebox import McpClient, McpError

RUNS = 5
SERVERS = [
    ("Plain test server", [sys.executable, "tests/fake_mcp_server.py", "noisy"], "double", {"number": 2}),
    ("SDK v2, flushed", [sys.executable, "chatty_server.py", "flushed"], "get_rota", {}),
    ("SDK v2, 20,000 lines", [sys.executable, "chatty_server.py", "many"], "get_rota", {}),
]
if len(sys.argv) > 1:
    SERVERS += [
        ("SDK v1, flushed", [sys.argv[1], "older_chatty.py", "flushed"], "get_rota", {}),
        ("SDK v1, 20,000 lines", [sys.argv[1], "older_chatty.py", "many"], "get_rota", {}),
    ]

print(f"{'Server':<22} {'answered':<10} noise lines per run")
for label, command, name, arguments in SERVERS:
    answered, counts, why = 0, [], ""
    for _ in range(RUNS):
        with McpClient(command, timeout=5) as server:
            try:
                server.call(name, arguments)
                answered += 1
            except McpError as error:
                why = str(error)
            counts.append(len(server.noise))
    print(f"{label:<22} {f'{answered} of {RUNS}':<10} {min(counts)} to {max(counts)}")
    if why:
        print(f"  {why}")
