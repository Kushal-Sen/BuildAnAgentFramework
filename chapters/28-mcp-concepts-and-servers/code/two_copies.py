"""Two copies of a pretend server behind a load balancer. No MCP here: only the question of where a session lives."""
from itertools import cycle

NEW = {"protocolVersion": "2026-07-28"}


class Copy:
    def __init__(self, name):
        self.name = name
        self.sessions = set()  # Lives in this copy's memory, so the other copy can't see it.
        self.served = 0

    def remembered(self, session):
        """The older way: the request names a session, and this copy must remember it."""
        if session not in self.sessions:
            return f"{self.name}: unknown session"
        self.served += 1
        return f"{self.name}: ok"

    def self_contained(self, request):
        """The stateless way: everything needed comes with the request."""
        if "protocolVersion" not in request:
            return f"{self.name}: refused"
        self.served += 1
        return f"{self.name}: ok"


a, b = Copy("A"), Copy("B")
turns = cycle([a, b])  # The balancer: each request goes to the next copy.
next(turns).sessions.add("s1")  # The handshake lands on A.
print("1. Session remembered by copy A, balancer takes turns")
print("  " + " | ".join(next(turns).remembered("s1") for _ in range(4)))

print("2. Self-contained requests, balancer takes turns")
print("  " + " | ".join(next(turns).self_contained(NEW) for _ in range(4)))

print("3. Sticky routing: each client always goes to the copy that holds its session")
a, b = Copy("A"), Copy("B")
home = {"cafe-1": a, "cafe-2": b, "cafe-3": a}
traffic = {"cafe-1": 90, "cafe-2": 5, "cafe-3": 5}
for client, copy in home.items():
    copy.sessions.add(client)
    for _ in range(traffic[client]):
        copy.remembered(client)
print(f"  100 requests: A served {a.served}, B served {b.served}")
a, b = Copy("A"), Copy("B")
turns = cycle([a, b])
for _ in range(100):
    next(turns).self_contained(NEW)
print(f"  Self-contained, taking turns: A served {a.served}, B served {b.served}")

print("4. Restart copy A: memory is wiped")
a = Copy("A")
a.sessions.add("s1")
print("  before: " + a.remembered("s1"))
a = Copy("A")
print("  after:  " + a.remembered("s1"))
print("  self-contained after: " + a.self_contained(NEW))

print("5. A shared store, as teams built with Redis: it works, and it's one more service to run")
shared = {"s1"}
a.sessions = b.sessions = shared
print("  " + " | ".join(copy.remembered("s1") for copy in (a, b)))
