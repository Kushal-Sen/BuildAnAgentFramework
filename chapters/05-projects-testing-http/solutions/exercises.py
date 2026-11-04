"""Chapter 05 exercises, solved."""


def read_response(response):
    if response.status_code == 200:
        return response.json()
    return f"Error: {response.status_code}"


def fetch_version(get):
    return get("http://127.0.0.1:11434/api/version", timeout=5).json()["version"]


def send_json(post, url, data):
    return post(url, json=data).json()


def checked_quantity(quantity):
    if quantity < 1:
        raise ValueError("quantity must be at least 1")
    return quantity
