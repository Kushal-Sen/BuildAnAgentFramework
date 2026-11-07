"""The first request sets which protocol a connection speaks. Each case here is one new connection."""
from by_hand import request
from real_errors import attempt

ROTA = {"name": "get_rota", "arguments": {"staff_number": "1042"}}

attempt("Forget _meta, then send a good request", request(1, "tools/list", new=False), request(2, "tools/call", **ROTA))
attempt("A harmless ping with no _meta, then a good request", request(1, "ping", new=False),
        request(2, "tools/call", **ROTA))
attempt("A good request, then forget _meta", request(1, "tools/call", **ROTA),
        request(2, "tools/call", new=False, **ROTA))
