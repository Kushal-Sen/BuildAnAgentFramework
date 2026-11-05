"""The checks for exercises.py. You don't need to change this file.

They use a fake model that gives scripted replies, so Ollama doesn't need to be running.
"""
from exercises import clear_changes, equals_number, failed_checks, steps_at_most, tool_count

from whitebox import Agent, Case, FakeModel, Message, ToolCall, contains, finished, run_eval
from whitebox.agent import Result


def answered(text, steps=1, calls=()):
    tool_calls = [ToolCall(name, {}) for name in calls]
    return Result(text, [Message("assistant", tool_calls=tool_calls)], steps)


def report_of(*answers, label="test"):
    """Run one case on scripted answers, and return the report."""
    model = FakeModel([Message("assistant", answer) for answer in answers])
    case = Case("sum", "Add.", [contains("380"), finished()])
    return run_eval(Agent(model), [case], runs=len(answers), label=label)


def test_todo_1_equals_number():
    check = equals_number(380)
    assert check.label == "equals 380"
    assert check.test(answered("The total is 380."))
    assert check.test(answered("It came to $380.00 in all."))
    assert not check.test(answered("The total is $1,380."))
    assert not check.test(answered("The total is 3800."))


def test_todo_2_steps_at_most():
    check = steps_at_most(6)
    assert check.label == "at most 6 steps"
    assert check.test(answered("Done", steps=6))
    assert not check.test(answered("Done", steps=7))


def test_todo_3_tool_count():
    check = tool_count("read_file", 3)
    assert check.label == "used read_file 3 times"
    assert check.test(answered("Done", calls=["list_files", "read_file", "read_file", "read_file"]))
    assert not check.test(answered("Done", calls=["read_file"]))


def test_todo_4_failed_checks():
    assert failed_checks(report_of("380", "381", "382")) == {"contains '380'": 2}
    assert failed_checks(report_of("380")) == {}


def test_todo_5_clear_changes():
    before = report_of("0", "0", "0", "380")
    after = report_of("380", "380", "380", "380")
    assert clear_changes(before, after, 2) == ["sum"]
    assert clear_changes(after, before, 2) == ["sum"]
    assert clear_changes(before, after, 3) == []
