"""Provided: LoopGuard stops a repeated call. The model is simulated, and the tools are real.

usage: python3 try_guard.py
"""
from sales_tools import toolbox
from whitebox import Agent, FakeModel, LoopGuard, Message, Printer, ToolCall

LIST_AGAIN = Message("assistant", tool_calls=[ToolCall("list_files", {"folder": "sales"})])

model = FakeModel([LIST_AGAIN, LIST_AGAIN, LIST_AGAIN, Message("assistant", "I'll try something else.")])
agent = Agent(model, toolbox, hooks=[Printer(), LoopGuard(limit=2)])
print(agent.run("What's in sales?").answer)
