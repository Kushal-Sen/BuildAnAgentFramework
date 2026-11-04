"""The checks for exercises.py. You don't need to change this file."""
import pytest

from exercises import add_turn, apply_temperature, estimate_tokens, fits_window, most_likely


def test_todo_1_estimate_tokens():
    assert estimate_tokens("Hello") == 2
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("") == 0


def test_todo_2_most_likely():
    assert most_likely({" Paris": 0.55, " a": 0.2, " the": 0.25}) == " Paris"


def test_todo_3_apply_temperature():
    even = apply_temperature([1, 1], 1)
    assert even == pytest.approx([0.5, 0.5])
    normal = apply_temperature([2, 1], 1)
    assert sum(normal) == pytest.approx(1)
    low = apply_temperature([2, 1], 0.1)
    high = apply_temperature([2, 1], 10)
    assert low[0] > normal[0] > high[0], "a low temperature should favor the top score"


def test_todo_4_fits_window():
    assert fits_window(3000, 1000, 4096) is True
    assert fits_window(4000, 200, 4096) is False


def test_todo_5_add_turn():
    history = [{"role": "user", "content": "Hi"}]
    result = add_turn(history, "Name?", "Asha")
    assert result[1] == {"role": "user", "content": "Name?"}
    assert result[2] == {"role": "assistant", "content": "Asha"}
    assert len(history) == 1, "don't change the original list"
