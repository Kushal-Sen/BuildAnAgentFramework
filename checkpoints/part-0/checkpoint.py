"""Part 0 checkpoint. Complete each TODO, then run: python3 -m pytest test_checkpoint.py"""
import functools
import json
from dataclasses import dataclass
from pathlib import Path

CALLS = []


@dataclass
class Order:
    """TODO 1: Add three fields: product (str), price (float) and quantity (int).
    Then add a total() method that returns price * quantity.
    """


def load_orders(path):
    """TODO 2: Read a JSON list of orders from the path, and return a list of Order objects.
    Each item has the keys product, price and quantity. Tip: Order(**item).
    If the file doesn't exist, return an empty list.
    """
    return None


def logged(function):
    """TODO 3: Return a wrapper that adds the function's name to CALLS,
    then calls the function and returns its result. Use functools.wraps.
    """
    return function


def big_orders(orders, minimum):
    """TODO 4: Write a generator that yields each order whose total is at least minimum."""
    return []


def fetch_json(get, url):
    """TODO 5: Call get(url, timeout=5). If the status code is 200, return the JSON.
    Otherwise, return "Error: 500", using the real status code.
    """
    return None
