"""Provided: rescue a tool call written as text. The model is simulated, and the tools are real.

usage: python3 try_rescue.py
"""
from sales_tools import toolbox
from whitebox import Agent, FakeModel, Message, Printer, RescueToolCalls

TEXT_CALL = '{"name": "list_files", "arguments": {"folder": "sales"}}'


def scripted():
    return FakeModel([Message("assistant", TEXT_CALL), Message("assistant", "There are three files.")])


print("Without RescueToolCalls:")
print(Agent(scripted(), toolbox, hooks=[Printer()]).run("What's in sales?").answer)

print("With RescueToolCalls:")
print(Agent(RescueToolCalls(scripted()), toolbox, hooks=[Printer()]).run("What's in sales?").answer)
