"""Provided: a generator only runs when you read it. This uses a fake model, not Ollama."""
from sales_tools import toolbox
from whitebox import Agent, FakeModel, Message, ToolCall

replies = [
    Message("assistant", tool_calls=[ToolCall("list_files", {"folder": "sales"})]),
    Message("assistant", "There are three files."),
]
model = FakeModel(replies)
events = Agent(model, toolbox).stream("How many files are there?")
print("Model calls after stream():", len(model.seen))
print("First event:", next(events).kind)
print("Model calls after one event:", len(model.seen))
print("The rest:", [event.kind for event in events])
print("Model calls at the end:", len(model.seen))
