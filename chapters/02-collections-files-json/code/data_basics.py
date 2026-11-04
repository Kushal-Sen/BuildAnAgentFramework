"""Collections, files, JSON and errors."""
import json
from pathlib import Path

HERE = Path(__file__).parent

# Lists
products = ["Coffee", "Tea"]
products.append("Juice")
print(products[0], len(products))

# Dictionaries
order = {"product": "Coffee", "quantity": 2}
order["price"] = 120
print(order["product"], order.get("discount", 0))

# A list of dictionaries
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
]
for message in messages:
    print(f"{message['role']}: {message['content']}")

# List comprehensions
prices = [120, 80, 95]
print([price * 2 for price in prices], sum(prices))

# Files
notes = HERE / "notes.txt"
notes.write_text("Order more coffee\n")
print(notes.read_text().strip())

# JSON
orders = json.loads((HERE / "orders.json").read_text())
print(sum(item["price"] * item["quantity"] for item in orders))
print(json.dumps({"name": "add", "arguments": {"a": 2, "b": 3}}))


# Errors
def read_json(path):
    """Return the data in a JSON file, or an error message."""
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        return f"Error: {path} doesn't exist"


print(read_json("missing.json"))
