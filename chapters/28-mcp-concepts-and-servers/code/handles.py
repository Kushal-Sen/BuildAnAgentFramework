"""Two real copies of basket_server.py, taking turns. The handle is an ordinary argument on every call."""
import json
from pathlib import Path

from by_hand import read, request, send, start, stop


def call(server, name, **arguments):
    send(server, request(1, "tools/call", name=name, arguments=arguments))
    return json.loads(read(server))["result"]["content"][0]["text"]


def shop(where):
    Path("baskets.json").unlink(missing_ok=True)
    print(f"Baskets kept in {where}")
    a, b = start("basket_server.py", where, timeout=20), start("basket_server.py", where, timeout=20)
    handle = call(a, "new_basket")
    print(f"  copy A: new_basket -> {handle}")
    for copy, name, item in ((b, "B", "flat white"), (a, "A", "oat milk"), (b, "B", "almond croissant")):
        print(f"  copy {name}: add {item} -> {call(copy, 'add_to_basket', basket=handle, item=item)}")
    stop(a)
    stop(b)


shop("memory")
shop("file")
