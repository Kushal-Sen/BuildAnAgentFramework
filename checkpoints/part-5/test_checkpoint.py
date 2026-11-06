"""The checks for checkpoint.py. You don't need to change this file."""
from checkpoint import (
    DEPOSITS, SYSTEM, Bank, build_agent, build_planner, deposit_tool, finish, left_to_pay, safe_tool,
)
from whitebox import (
    Checkpoint, Chunk, FakeEmbedder, FakeModel, Index, Memory, Message, Plan, RescueToolCalls, Retry, ToolCall, Trim,
)


def pay(*members):
    return Message("assistant", tool_calls=[ToolCall("return_deposit", {"member": member}) for member in members])


def desk(tmp_path, replies, deposit=None):
    bank = Bank(tmp_path / "bank.jsonl")
    tool = deposit or deposit_tool(bank)
    agent = build_agent(FakeModel(replies), Memory(tmp_path / "notes.json"), [tool], tmp_path / "run.json")
    return agent, bank


def test_todo_1_build_agent(tmp_path):
    memory = Memory(tmp_path / "notes.json")
    memory.add("I'm Rosa, and I run the Saturday desk.")
    agent = build_agent(FakeModel([]), memory, [deposit_tool(Bank(tmp_path / "bank.jsonl"))], tmp_path / "run.json")
    assert isinstance(agent.model, Retry) and isinstance(agent.model.model, RescueToolCalls)
    assert SYSTEM in agent.system and "Rosa" in agent.system
    assert set(agent.toolbox.tools) == {"remember", "return_deposit"}
    assert memory in agent.hooks
    assert {type(hook) for hook in agent.hooks} >= {Trim, Checkpoint}
    assert agent.max_steps == 16 and agent.options == {"temperature": 0.7}


def test_todo_2_safe_tool(tmp_path):
    bank = Bank(tmp_path / "bank.jsonl")
    deposit = safe_tool(deposit_tool(bank), bank)
    deposit(member="L-201")
    deposit(member="L-201")
    assert bank.paid() == ["L-201"]
    assert deposit.name == "return_deposit"


def test_todo_3_left_to_pay(tmp_path):
    bank = Bank(tmp_path / "bank.jsonl")
    assert left_to_pay(bank) == list(DEPOSITS)
    bank.pay("L-202")
    assert left_to_pay(bank) == ["L-201", "L-203", "L-204", "L-205"]


def test_todo_4_finish_trusts_the_bank(tmp_path):
    replies = [Message("assistant", "All done!"), pay(*DEPOSITS), Message("assistant", "DONE")]
    agent, bank = desk(tmp_path, replies)
    finish(agent, bank, tmp_path / "run.json")
    assert sorted(bank.paid()) == sorted(DEPOSITS)
    assert "L-205" in agent.model.model.model.seen[0][-1].content


def test_todo_4_finish_resumes_from_a_save(tmp_path):
    Checkpoint(tmp_path / "run.json").save([Message("system", "Saved rules."), Message("user", "Saved task.")])
    agent, bank = desk(tmp_path, [pay(*DEPOSITS), Message("assistant", "DONE")])
    finish(agent, bank, tmp_path / "run.json")
    assert agent.model.model.model.seen[0][0].content == "Saved rules."


def test_todo_5_build_planner():
    index = Index(FakeEmbedder())
    index.add([Chunk("Deposits are returned at the desk.", "deposits.md")])
    planner = build_planner(FakeModel([]), index)
    assert isinstance(planner, Plan)
    assert planner.k == 3 and planner.options == {"temperature": 0.7}
