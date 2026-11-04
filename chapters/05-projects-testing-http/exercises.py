"""Chapter 05 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py test_mine.py"""


def read_response(response):
    """TODO 1: If the status code is 200, return response.json().
    Otherwise, return "Error: 404", using the real status code.
    """
    return None


def fetch_version(get):
    """TODO 2: Call get("http://127.0.0.1:11434/api/version", timeout=5),
    and return the "version" value from its JSON.
    """
    return None


def send_json(post, url, data):
    """TODO 3: Call post with the url, send data using json=data, and return its JSON."""
    return None


def checked_quantity(quantity):
    """TODO 4: Raise a ValueError if quantity is below 1. Otherwise, return quantity."""
    return quantity
