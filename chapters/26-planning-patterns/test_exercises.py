"""The checks for exercises.py. You don't need to change this file.

They use a fake model and a fake embedder, so Ollama doesn't need to be running.
"""
from exercises import TidyPlan, calls_per_earned, drop_label, earned, plans_naming

from whitebox import Chunk, FakeEmbedder, FakeModel, Index, Message


def say(text):
    return Message("assistant", text)


def index():
    built = Index(FakeEmbedder())
    built.add([Chunk("Shift leads are Band C.", "pay-bands.md"), Chunk("Band C gives 4 weeks of notice.", "resignation.md")])
    return built


def test_todo_1_earned():
    seen = "[pay-bands.md]\nShift lead: Band C\n\n[resignation.md]\nBand C gives 4 weeks."
    assert earned(True, seen, ["pay-bands.md", "resignation.md"]) is True
    assert earned(False, seen, ["pay-bands.md", "resignation.md"]) is False
    assert earned(True, "[resignation.md]\nBand C gives 4 weeks.", ["pay-bands.md", "resignation.md"]) is False
    assert earned(True, "It mentions pay-bands.md and resignation.md in a sentence.", ["pay-bands.md"]) is False


def test_todo_2_calls_per_earned():
    assert calls_per_earned(60, 7) == 8.6
    assert calls_per_earned(210, 15) == 14.0
    assert calls_per_earned(60, 0) is None


def test_todo_3_drop_label():
    assert drop_label("Step 1: Find the band") == "Find the band"
    assert drop_label("STEP 2:  Find the notice") == "Find the notice"
    assert drop_label("1. Find the band") == "Find the band"
    assert drop_label("Find the rule: notice") == "Find the rule: notice"
    assert drop_label("Find the band") == "Find the band"


def test_todo_4_tidy_plan():
    model = FakeModel([say("Step 1: Find the band\nStep 2: Find the notice"), say("Shift leads are Band C."),
                       say("Band C notice"), say("4 weeks."), say("4 weeks.")])
    result = TidyPlan(model, index()).run("How much notice does a shift lead give?")
    assert result.plan == ["Find the band", "Find the notice"]
    assert result.queries[0] == "Find the band"
    assert "Step: Find the notice" in model.seen[2][0].content
    assert result.answer == "4 weeks."


def test_todo_5_plans_naming():
    plans = [["Find the BAND of a shift lead", "Find the notice"], ["Review the handbook"], [], ["Check the band", "Band rule"]]
    assert plans_naming(plans, "band") == 2
    assert plans_naming(plans, "handbook") == 1
    assert plans_naming(plans, "pension") == 0
