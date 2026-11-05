"""Provided: the same loop with two different models."""
from sales_tools import SCHEMAS, TOOLS
from whitebox import FakeModel, Message, OllamaModel, ToolCall, run_agent

QUESTION = "What was the coffee revenue in sales/monday.txt?"

real = OllamaModel("qwen2.5:7b")
fake = FakeModel([
    Message("assistant", tool_calls=[ToolCall("read_file", {"path": "sales/monday.txt"})]),
    Message("assistant", "This answer was written in advance."),
])

print("With OllamaModel")
print(run_agent(QUESTION, real, TOOLS, SCHEMAS, temperature=0))
print()
print("With FakeModel")
print(run_agent(QUESTION, fake, TOOLS, SCHEMAS))
print("The fake was called", len(fake.seen), "times.")
print("On its last call, it saw", len(fake.seen[-1]), "messages.")
