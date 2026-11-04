"""The checks for exercises.py. You don't need to change this file."""
from exercises import build_prompt, final_answer, label_schema, parse_json, with_examples


def test_todo_1_build_prompt():
    expected = "Task: Write a sign\nContext: A coffee shop\nFormat: One sentence"
    assert build_prompt("Write a sign", "A coffee shop", "One sentence") == expected


def test_todo_2_with_examples():
    result = with_examples("Pick a label.", [("I need a refund.", "billing"), ("It broke.", "bug")])
    assert result == ("Pick a label.\nMessage: I need a refund. Label: billing\n"
                      "Message: It broke. Label: bug")


def test_todo_3_final_answer():
    assert final_answer("First, add.\nThen subtract.\n  503  \n") == "503"


def test_todo_4_parse_json():
    assert parse_json('{"a": 1}') == {"a": 1}
    assert parse_json('```json\n{"a": 1}\n```\n') == {"a": 1}


def test_todo_5_label_schema():
    assert label_schema(["bug", "other"]) == {
        "type": "object",
        "properties": {"label": {"type": "string", "enum": ["bug", "other"]}},
        "required": ["label"],
    }
