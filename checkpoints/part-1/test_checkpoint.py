"""The checks for checkpoint.py. You don't need to change this file."""
import inspect
import json

from checkpoint import LABELS, classify, classify_all, count_labels, ticket_messages, ticket_schema


def fake_chat(messages, format=None, **options):
    assert format == ticket_schema(), "pass format=ticket_schema()"
    assert options.get("temperature") == 0, "pass temperature=0"
    return json.dumps({"label": "bug"})


def test_todo_1_ticket_schema():
    schema = ticket_schema()
    assert schema["properties"]["label"]["enum"] == LABELS
    assert schema["required"] == ["label"]


def test_todo_2_ticket_messages():
    first, second = ticket_messages("It broke.")
    assert first["role"] == "system"
    assert all(label in first["content"] for label in LABELS), "define every label"
    assert second == {"role": "user", "content": "It broke."}


def test_todo_3_classify():
    assert classify(fake_chat, "It broke.") == "bug"


def test_todo_4_classify_all():
    result = classify_all(fake_chat, ["A", "B"])
    assert inspect.isgenerator(result), "use yield"
    assert list(result) == [("A", "bug"), ("B", "bug")]


def test_todo_5_count_labels():
    assert count_labels([("A", "bug"), ("B", "bug"), ("C", "other")]) == {"bug": 2, "other": 1}
