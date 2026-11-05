"""The checks for exercises.py. You don't need to change this file.

They use a fake model that gives scripted replies, so Ollama doesn't need to be running.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))  # So Python can find whitebox.

from typing import Annotated

from exercises import Conversation, WordModel, run_live, tool_names
from whitebox import Agent, FakeModel, Message, ToolCall, Toolbox, tool


@tool
def double(number: Annotated[int, "The number to double"]) -> int:
    """Double a number."""
    return number * 2


toolbox = Toolbox([double])
ASK = Message("assistant", tool_calls=[ToolCall("double", {"number": 4})])
ANSWER = Message("assistant", "It's 8.")


def test_todo_1_word_model():
    pieces = list(WordModel([ANSWER]).stream([]))
    assert pieces == ["It's ", "8. ", ANSWER]
    events = Agent(WordModel([ANSWER]), toolbox).stream("Double 4.")
    assert [event.kind for event in events] == ["text", "text", "done"]


def test_todo_2_tool_names():
    events = Agent(FakeModel([ASK, ASK, ANSWER]), toolbox).stream("Double 4, twice.")
    assert tool_names(events) == ["double", "double"]


def test_todo_3_run_live():
    shown = []
    result = run_live(Agent(WordModel([ASK, ANSWER]), toolbox), "Double 4.", shown.append)
    assert shown == ["It's ", "8. "]
    assert result.answer == "It's 8." and result.steps == 2


def test_todo_4_conversation_remembers():
    model = FakeModel([ANSWER, Message("assistant", "Yes.")])
    conversation = Conversation(Agent(model, toolbox))
    assert conversation.ask("Double 4.") == "It's 8."
    assert conversation.ask("Sure?") == "Yes."
    assert [message.content for message in model.seen[1]][1:] == ["Double 4.", "It's 8.", "Sure?"]


def test_todo_5_transcript():
    conversation = Conversation(Agent(FakeModel([ASK, ANSWER]), toolbox))
    conversation.ask("Double 4.")
    assert conversation.transcript() == ["user: Double 4.", "tool: 8", "assistant: It's 8."]
