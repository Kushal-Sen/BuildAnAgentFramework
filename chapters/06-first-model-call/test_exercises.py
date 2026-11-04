"""The checks for exercises.py. You don't need to change this file."""
import json

from exercises import build_body, join_stream, reply_text, user_message, with_system


def test_todo_1_user_message():
    assert user_message("Hi") == {"role": "user", "content": "Hi"}


def test_todo_2_with_system():
    assert with_system("Be brief.", "Hi") == [
        {"role": "system", "content": "Be brief."},
        {"role": "user", "content": "Hi"},
    ]


def test_todo_3_build_body():
    messages = [{"role": "user", "content": "Hi"}]
    assert build_body("qwen2.5:7b", messages) == {
        "model": "qwen2.5:7b", "messages": messages, "stream": False,
    }


def test_todo_4_reply_text():
    assert reply_text({"message": {"role": "assistant", "content": "Hello"}}) == "Hello"


def test_todo_5_join_stream():
    lines = [json.dumps({"message": {"content": piece}}) for piece in ["Hel", "lo", "!"]]
    assert join_stream(lines) == "Hello!"
