"""The checks for exercises.py. These use a fake model, so Ollama doesn't need to be running."""
from exercises import ask_model, give_result, pick_shape, play_session, workflow_prompt


def fake_model(replies):
    """Return a chat function that gives these replies in order, and notes what it was sent."""
    seen = []

    def chat(messages):
        seen.append(len(messages))
        return replies[len(seen) - 1]

    chat.seen = seen
    return chat


def test_todo_1_ask_model():
    messages = [{"role": "user", "content": "Hi"}]
    assert ask_model(messages, fake_model(["Hello"])) == "Hello"
    assert messages[-1] == {"role": "assistant", "content": "Hello"}


def test_todo_2_give_result():
    messages = []
    give_result(messages, "Coffee: 120")
    assert messages == [{"role": "user", "content": "Coffee: 120"}]


def test_todo_3_play_session():
    chat = fake_model(["Which files?", "What's in a.txt?", "The total is 120."])
    assert play_session("Total?", chat, ["a.txt", "Coffee: 120"]) == "The total is 120."
    assert chat.seen == [1, 3, 5]


def test_todo_4_workflow_prompt():
    files = {"b.txt": "Coffee: 150", "a.txt": "Coffee: 120"}
    assert workflow_prompt("Total?", files) == "Total?\n\na.txt: Coffee: 120\nb.txt: Coffee: 150"


def test_todo_5_pick_shape():
    assert pick_shape(False, True) == "single call"
    assert pick_shape(False, False) == "single call"
    assert pick_shape(True, True) == "workflow"
    assert pick_shape(True, False) == "agent"
