"""Chapter 15 exercises, worked answers."""
from whitebox import FakeModel


class WordModel(FakeModel):
    def stream(self, messages, tools=None, **options):
        reply = self.chat(messages, tools, **options)
        for word in reply.content.split():
            yield word + " "
        yield reply


def tool_names(events):
    return [event.call.name for event in events if event.kind == "tool_call"]


def run_live(agent, question, show):
    for event in agent.stream(question):
        if event.kind == "text":
            show(event.text)
        elif event.kind == "done":
            return event.result


class Conversation:
    """An agent that remembers. The agent itself keeps nothing between runs."""

    def __init__(self, agent):
        self.agent = agent
        self.history = None

    def ask(self, question):
        result = self.agent.run(question, self.history)
        self.history = result.messages
        return result.answer

    def transcript(self):
        return [
            f"{message.role}: {message.content}"
            for message in self.history
            if message.role != "system" and message.content
        ]
