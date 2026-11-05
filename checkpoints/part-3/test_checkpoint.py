"""The checks for checkpoint.py. You don't need to change this file."""
import checkpoint
from checkpoint import CountingModel, ToolCounter, build_agent, make_cases
from whitebox import Agent, FakeModel, LoopGuard, Message, Retry, ToolCall
from whitebox.agent import Result


def test_todo_1_find_lines():
    assert checkpoint.find_lines("trip/day1.txt", "food") == "Food: 35"
    assert checkpoint.find_lines("trip/day1.txt", "plane") == ""
    schema = checkpoint.find_lines.parameters
    assert sorted(schema["required"]) == ["path", "word"]


def test_todo_2_counting_model():
    answer = Message("assistant", "Hi")
    model = CountingModel(FakeModel([answer, answer]))
    assert model.chat([]) == answer
    assert list(model.stream([])) == ["Hi", answer]
    assert model.calls == 2


def test_todo_3_tool_counter():
    asking = Message("assistant", tool_calls=[ToolCall("add_numbers", {"numbers": [1, 2]})])
    counter = ToolCounter()
    fake = FakeModel([asking, asking, Message("assistant", "3")])
    build_agent(fake, counter).run("Add.")
    assert counter.counts == {"add_numbers": 2}


def test_todo_4_build_agent():
    counter = ToolCounter()
    agent = build_agent(FakeModel([]), counter)
    assert isinstance(agent, Agent) and isinstance(agent.model, Retry)
    assert sorted(agent.toolbox.tools) == ["add_numbers", "find_lines", "list_files"]
    assert counter in agent.hooks and any(isinstance(hook, LoopGuard) for hook in agent.hooks)
    assert agent.options == {"temperature": 0.7}


def test_todo_5_make_cases():
    food, hotel = make_cases()
    assert (food.name, hotel.name) == ("food total", "hotel total")
    used = [Message("assistant", tool_calls=[ToolCall("find_lines", {})])]
    assert all(check.test(Result("It was 105.", used, 3)) for check in food.checks)
    assert all(check.test(Result("It was 180.", used, 3)) for check in hotel.checks)
    assert not all(check.test(Result("It was 99.", used, 3)) for check in food.checks)
    assert not all(check.test(Result("It was 105.", [], 3)) for check in food.checks)
    assert not all(check.test(Result("It was 105.", used, 3, stopped=True)) for check in food.checks)
