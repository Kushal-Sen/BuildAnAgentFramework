"""What the code does with one reply that asks for 2,000 payments. It's a fake model, so no Ollama is needed."""
import tempfile

from refunds import ORDERS, Bank, refund_tools
from whitebox import Agent, FakeModel, LoopGuard, Message, ToolCall, Toolbox, once

CALLS = 2000
orders = list(ORDERS) * (CALLS // len(ORDERS) + 1)
runaway = Message("assistant", tool_calls=[ToolCall("issue_refund", {"order": order}) for order in orders[:CALLS]])


def run(label, safe=False, hooks=()):
    with tempfile.TemporaryDirectory() as folder:
        bank = Bank(folder)
        _, issue_refund = refund_tools(bank)
        tool = once(issue_refund, bank.paid) if safe else issue_refund
        model = FakeModel([runaway, Message("assistant", "DONE")])
        result = Agent(model, Toolbox([tool]), max_steps=16, hooks=list(hooks)).run("Process today's refunds.")
        print(f"{label:<12} replies {result.steps}, stopped by max_steps: {result.stopped}, payments {len(bank.payments())}")


run("plain tool")
run("LoopGuard", hooks=[LoopGuard()])
run("once", safe=True)
