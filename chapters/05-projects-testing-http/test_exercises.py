"""The checks for exercises.py. You don't need to change this file."""
import pytest

from exercises import checked_quantity, fetch_version, read_response, send_json


class FakeResponse:
    """Stands in for a real response, so these tests need no network."""

    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        return self.data


def test_todo_1_read_response():
    assert read_response(FakeResponse(200, {"a": 1})) == {"a": 1}
    assert read_response(FakeResponse(404, {})) == "Error: 404"


def test_todo_2_fetch_version():
    def fake_get(url, timeout):
        assert url.endswith("/api/version")
        return FakeResponse(200, {"version": "1.2.3"})

    assert fetch_version(fake_get) == "1.2.3"


def test_todo_3_send_json():
    def fake_post(url, json):
        return FakeResponse(200, {"url": url, "got": json})

    assert send_json(fake_post, "http://x", {"a": 1}) == {"url": "http://x", "got": {"a": 1}}


def test_todo_4_checked_quantity():
    assert checked_quantity(2) == 2
    with pytest.raises(ValueError):
        checked_quantity(0)
