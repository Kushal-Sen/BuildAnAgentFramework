"""Provided: five failures with no safety nets. Only the first is real, the rest are simulated.

usage: python3 failures.py
"""
import time
from typing import Annotated

from sales_tools import toolbox
from whitebox import Agent, FakeModel, Message, ModelError, OllamaModel, ToolCall, Toolbox, tool

QUESTION = "What was the total coffee revenue across all the days in the sales folder?"
TEXT_CALL = '{"name": "list_files", "arguments": {"folder": "sales"}}'
LIST_AGAIN = Message("assistant", tool_calls=[ToolCall("list_files", {"folder": "sales"})])


@tool
def slow_lookup(order: Annotated[str, "The order number, such as A17"]) -> str:
    """Look up an order. This one takes far too long."""
    time.sleep(3)
    return "Delivered"


print("1. Ollama can't be reached (real: nothing is listening on this port)")
broken = OllamaModel("qwen2.5:7b", url="http://127.0.0.1:9")
try:
    Agent(broken, toolbox).run(QUESTION)
except ModelError as error:
    print("   Crashed:", str(error)[:62], "...")

print("2. The model sends an empty reply (simulated)")
result = Agent(FakeModel([Message("assistant")]), toolbox).run(QUESTION)
print(f"   Answer: {result.answer!r}")

print("3. The model writes a tool call as text (simulated)")
result = Agent(FakeModel([Message("assistant", TEXT_CALL)]), toolbox).run(QUESTION)
print(f"   Answer: {result.answer!r}")

print("4. The model repeats the same call (simulated)")
result = Agent(FakeModel([LIST_AGAIN] * 8), toolbox).run(QUESTION)
print(f"   Answer: {result.answer!r}")

print("5. A tool hangs (simulated: it only sleeps for 3 seconds)")
ask = Message("assistant", tool_calls=[ToolCall("slow_lookup", {"order": "A17"})])
started = time.monotonic()
Agent(FakeModel([ask, Message("assistant", "Delivered.")]), Toolbox([slow_lookup])).run("Where's A17?")
print(f"   The agent sat waiting for {time.monotonic() - started:.0f} seconds")
