"""The checks for checkpoint.py. You don't need to change this file."""
from checkpoint import SYSTEM, build_agent, build_chunks, build_index, build_pipeline, make_cases
from whitebox import (
    Agent, FakeEmbedder, FakeModel, HybridIndex, Index, KeywordIndex, LoopGuard, Message, Rag, RescueToolCalls, Retry,
)
from whitebox.agent import Result


def index():
    return build_index(build_chunks(), FakeEmbedder())


def test_todo_1_build_chunks():
    chunks = build_chunks()
    assert len(chunks) >= 7
    assert {chunk.source for chunk in chunks} >= {"late-fees.md", "membership.md"}
    assert all(chunk.text.lstrip("# ").startswith(("Membership", "Late", "Loans", "Opening", "Printing", "Meeting", "Lost"))
               for chunk in chunks)


def test_todo_2_build_index():
    built = index()
    assert isinstance(built, HybridIndex)
    assert sorted(type(part).__name__ for part in built.indexes) == ["Index", "KeywordIndex"]
    assert built.search("Oak Room seats", 1)[0].source == "rooms.md"


def test_todo_3_build_pipeline():
    model = FakeModel([Message("assistant", "40p")])
    pipeline = build_pipeline(model, index())
    assert isinstance(pipeline, Rag)
    assert pipeline.k == 3 and pipeline.options == {"temperature": 0.7}
    assert pipeline.run("colour printing").answer == "40p"


def test_todo_4_build_agent():
    agent = build_agent(FakeModel([]), index())
    assert isinstance(agent, Agent) and isinstance(agent.model, Retry)
    assert isinstance(agent.model.model, RescueToolCalls)
    assert list(agent.toolbox.tools) == ["search_handbook"]
    assert agent.system == SYSTEM and agent.options == {"temperature": 0.7}
    assert any(isinstance(hook, LoopGuard) for hook in agent.hooks)


def test_todo_5_make_cases():
    page, fee, cafe = make_cases()
    assert (page.name, fee.name, cafe.name) == ("colour page", "student fee", "cafe")
    assert all(check.test(Result("It's 40p.", [], 1)) for check in page.checks)
    assert all(check.test(Result("It's 5p a day.", [], 2)) for check in fee.checks)
    assert all(check.test(Result("I don't know.", [], 1)) for check in cafe.checks)
    assert not all(check.test(Result("It's 15p.", [], 1)) for check in page.checks)
    assert not all(check.test(Result("It's 5p.", [], 2, stopped=True)) for check in fee.checks)
    assert not all(check.test(Result("Band A pays 5p, Band B 10p and Band C 20p.", [], 2)) for check in fee.checks)
