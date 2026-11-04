"""The checks for checkpoint.py. You don't need to change this file."""
import inspect
import json

from checkpoint import CALLS, Order, big_orders, fetch_json, load_orders, logged


class FakeResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        return self.data


def test_todo_1_order():
    assert Order("Tea", 80, 3).total() == 240


def test_todo_2_load_orders(tmp_path):
    path = tmp_path / "orders.json"
    path.write_text(json.dumps([{"product": "Tea", "price": 80, "quantity": 3}]))
    assert load_orders(path) == [Order("Tea", 80, 3)]
    assert load_orders(tmp_path / "missing.json") == []


def test_todo_3_logged():
    @logged
    def add(a, b):
        return a + b

    assert add(2, b=3) == 5
    assert CALLS[-1] == "add"
    assert add.__name__ == "add"


def test_todo_4_big_orders():
    orders = [Order("Tea", 80, 1), Order("Coffee", 120, 3)]
    result = big_orders(orders, 100)
    assert inspect.isgenerator(result)
    assert list(result) == [orders[1]]


def test_todo_5_fetch_json():
    assert fetch_json(lambda url, timeout: FakeResponse(200, {"a": 1}), "http://x") == {"a": 1}
    assert fetch_json(lambda url, timeout: FakeResponse(500, {}), "http://x") == "Error: 500"
