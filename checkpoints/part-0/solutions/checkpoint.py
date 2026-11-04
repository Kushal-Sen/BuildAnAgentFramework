"""Part 0 checkpoint, solved."""
import functools
import json
from dataclasses import dataclass
from pathlib import Path

CALLS = []


@dataclass
class Order:
    product: str
    price: float
    quantity: int

    def total(self) -> float:
        return self.price * self.quantity


def load_orders(path):
    try:
        items = json.loads(Path(path).read_text())
    except FileNotFoundError:
        return []
    return [Order(**item) for item in items]


def logged(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        CALLS.append(function.__name__)
        return function(*args, **kwargs)

    return wrapper


def big_orders(orders, minimum):
    for order in orders:
        if order.total() >= minimum:
            yield order


def fetch_json(get, url):
    response = get(url, timeout=5)
    if response.status_code == 200:
        return response.json()
    return f"Error: {response.status_code}"
