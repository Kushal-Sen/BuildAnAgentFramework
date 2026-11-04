"""Chapter 02 exercises, solved. Run: python3 solutions/exercises.py"""
import json
import tempfile
from pathlib import Path


def total_quantity(orders):
    """Add up the "quantity" of every dictionary in the list."""
    return sum(order["quantity"] for order in orders)


def get_price(prices, product):
    """Return the product's price from the dictionary, or 0 if it isn't there."""
    return prices.get(product, 0)


def in_stock(products):
    """Return the "name" of each product whose "stock" is above 0, as a list."""
    return [product["name"] for product in products if product["stock"] > 0]


def save_and_load(path, data):
    """Save data to the path as JSON, then read the file back and return the data."""
    Path(path).write_text(json.dumps(data))
    return json.loads(Path(path).read_text())


def tool_name(text):
    """Read JSON text and return its "name" value. For invalid JSON, return "Error: invalid JSON"."""
    try:
        return json.loads(text)["name"]
    except json.JSONDecodeError:
        return "Error: invalid JSON"


# ---- Self-check: you don't need to change anything below this line. ----

SAVE_PATH = str(Path(tempfile.gettempdir()) / "whitebox_chapter_02.json")
STOCK = [{"name": "Coffee", "stock": 4}, {"name": "Tea", "stock": 0}, {"name": "Juice", "stock": 1}]
CHECKS = [
    ("TODO 1: total_quantity", total_quantity, [(([{"quantity": 2}, {"quantity": 3}],), 5), (([],), 0)]),
    ("TODO 2: get_price", get_price, [(({"Tea": 80}, "Tea"), 80), (({"Tea": 80}, "Juice"), 0)]),
    ("TODO 3: in_stock", in_stock, [((STOCK,), ["Coffee", "Juice"]), (([],), [])]),
    ("TODO 4: save_and_load", save_and_load, [((SAVE_PATH, {"a": [1, 2]}), {"a": [1, 2]})]),
    ("TODO 5: tool_name", tool_name, [(('{"name": "add"}',), "add"), (("not json",), "Error: invalid JSON")]),
]


def run_check(cases, function):
    for arguments, expected in cases:
        result = function(*arguments)
        call = f"{function.__name__}({', '.join(repr(a) for a in arguments)})"
        call = call if len(call) < 50 else f"{function.__name__}(...)"
        assert result == expected, f"{call} returned {result!r}, expected {expected!r}"


if __name__ == "__main__":
    passed = 0
    for label, function, cases in CHECKS:
        try:
            run_check(cases, function)
            passed += 1
            print(f"PASS  {label}")
        except Exception as error:
            print(f"FAIL  {label}: {error}")
    print(f"{passed}/{len(CHECKS)} passed")
