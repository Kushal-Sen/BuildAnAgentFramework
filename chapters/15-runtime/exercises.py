"""Chapter 15 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
from whitebox import FakeModel


class WordModel(FakeModel):
    def stream(self, messages, tools=None, **options):
        """TODO 1: Get the next reply with self.chat(messages, tools, **options). Yield each
        word of its content, one at a time, with a space after each word. Then yield the
        whole reply. FakeModel gives every reply in one piece, and this model won't.
        """
        return iter([])


def tool_names(events):
    """TODO 2: Return the name of every tool the agent asked for, in order.
    Look for the events with the kind "tool_call". Each one has the tool call in event.call.
    """
    return None


def run_live(agent, question, show):
    """TODO 3: Stream the agent. Call show(text) for each "text" event, as it arrives.
    Return the Result from the "done" event.
    """
    return None


class Conversation:
    """An agent that remembers. The agent itself keeps nothing between runs."""

    def __init__(self, agent):
        self.agent = agent
        self.history = None

    def ask(self, question):
        """TODO 4: Run the agent with self.history, keep the new messages in self.history,
        and return the answer.
        """
        return None

    def transcript(self):
        """TODO 5: Return a list of "role: content" strings, one for each message in
        self.history. Leave out the system message, and any message with no content.
        """
        return None
