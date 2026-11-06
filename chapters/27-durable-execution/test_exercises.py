"""The checks for exercises.py. You don't need to change this file.

They use a fake model, so Ollama doesn't need to be running.
"""
from typing import Annotated

from exercises import CallLimit, repeats, resume, safe_email, still_left

from whitebox import Agent, Checkpoint, FakeModel, Message, ToolCall, Toolbox, tool


def pay_tool(bank):
    @tool
    def pay(order: Annotated[str, "The order number"]) -> str:
        """Pay one order."""
        bank.append(order)
        return f"Paid {order}."

    return pay


def calls(*orders):
    return Message("assistant", tool_calls=[ToolCall("pay", {"order": order}) for order in orders])


def test_todo_1_repeats():
    assert repeats(["A", "B", "C"]) == 0
    assert repeats(["A", "B", "A", "A"]) == 2
    assert repeats([]) == 0


def test_todo_2_resume(tmp_path):
    path = tmp_path / "run.json"
    model = FakeModel([Message("assistant", "Started.")])
    assert resume(Agent(model), path, "Start", "Carry on").answer == "Started."
    assert model.seen[0][-1].content == "Start"
    Checkpoint(path).save([Message("system", "Be kind."), Message("user", "Start")])
    model = FakeModel([Message("assistant", "Finished.")])
    assert resume(Agent(model), path, "Start", "Carry on").answer == "Finished."
    assert [message.content for message in model.seen[0]] == ["Be kind.", "Start", "Carry on"]


def test_todo_3_safe_email():
    sent = []

    @tool
    def send_email(customer: Annotated[str, "Who to email"], order: Annotated[str, "The order number"]) -> str:
        """Tell a customer their refund has gone."""
        sent.append((customer, order))
        return "Sent."

    safe = safe_email(send_email, sent)
    assert safe(customer="Ana", order="A") == "Sent."
    assert "Already done" in safe(customer="Ana", order="A")
    assert safe(customer="Ana", order="B") == "Sent."
    assert safe(customer="Bo", order="A") == "Sent."
    assert len(sent) == 3
    assert safe.name == "send_email"


def test_todo_4_still_left():
    bank = []
    wanted = lambda: [order for order in ["A", "B"] if order not in bank]  # noqa: E731
    ask = lambda orders: f"Still to pay: {orders}"  # noqa: E731
    model = FakeModel([Message("assistant", "All done!"), Message("assistant", "Yes, all done!")])
    agent = Agent(model, Toolbox([pay_tool(bank)]))
    assert still_left(agent, wanted, ask, tries=2) == ["A", "B"]
    assert model.replies == []
    model = FakeModel([calls("A", "B"), Message("assistant", "Done.")])
    assert still_left(Agent(model, Toolbox([pay_tool(bank)])), wanted, ask) == []
    assert bank == ["A", "B"]


def test_todo_5_call_limit():
    bank = []

    @tool
    def check(order: Annotated[str, "The order number"]) -> str:
        """Look at one order."""
        return "Fine."

    both = Message("assistant", tool_calls=[ToolCall("check", {"order": "A"})] + calls("A", "B", "C").tool_calls)
    hook = CallLimit("pay", 2)
    model = FakeModel([both, Message("assistant", "Done."), calls("D", "E", "F"), Message("assistant", "Done.")])
    agent = Agent(model, Toolbox([pay_tool(bank), check]), hooks=[hook])
    result = agent.run("Go")
    assert bank == ["A", "B"]
    outputs = [message.content for message in result.messages if message.role == "tool"]
    assert outputs == ["Fine.", "Paid A.", "Paid B.", "Error: too many calls to pay."]
    agent.run("Go again")
    assert bank == ["A", "B", "D", "E"]
