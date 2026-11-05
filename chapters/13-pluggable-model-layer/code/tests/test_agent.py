import pytest

from whitebox import FakeModel, Message, OllamaModel, ToolCall, load_model, run_agent


def double(number):
    return number * 2


def test_the_loop_runs_a_tool_then_answers():
    model = FakeModel([
        Message("assistant", tool_calls=[ToolCall("double", {"number": 4})]),
        Message("assistant", "It's 8."),
    ])
    assert run_agent("Double 4.", model, {"double": double}, []) == "It's 8."
    assert model.seen[1][-1] == Message("tool", "8", tool_name="double")


def test_the_step_limit_stops_the_loop():
    asking = Message("assistant", tool_calls=[ToolCall("double", {"number": 4})])
    model = FakeModel([asking, asking])
    answer = run_agent("Double 4.", model, {"double": double}, [], max_steps=2)
    assert answer == "Stopped: no answer after 2 steps."


def test_load_model_reads_the_provider_and_name():
    model = load_model("ollama/llama3.1:8b")
    assert isinstance(model, OllamaModel) and model.name == "llama3.1:8b"


def test_load_model_rejects_an_unknown_provider():
    with pytest.raises(ValueError, match="Unknown provider"):
        load_model("nobody/model")


def test_ollama_translation_round_trip():
    model = OllamaModel("x")
    data = {"content": "", "tool_calls": [{"function": {"name": "a", "arguments": {"b": 1}}}]}
    message = model.from_ollama(data)
    assert message.tool_calls == [ToolCall("a", {"b": 1})]
    assert model.to_ollama(message)["tool_calls"] == [{"function": {"name": "a", "arguments": {"b": 1}}}]
