"""The refund job's shared parts: six orders, a pretend bank, the two tools and the agent. Provided."""
import json
import os
import signal
import sys
from pathlib import Path
from typing import Annotated

from whitebox import Agent, RescueToolCalls, Retry, Toolbox, load_model, tool

ORDERS = {"QC-101": 4.50, "QC-102": 12.00, "QC-103": 3.20, "QC-104": 7.75, "QC-105": 18.40, "QC-106": 5.10}
SYSTEM = ("You process refunds. Call list_refunds, then call issue_refund for each order, one at a time. "
          "When every order is done, reply DONE.")
TASK = "Process today's refunds."
AGAIN = "You were interrupted. Carry on with the orders that aren't done yet, then reply DONE."
OPTIONS = {"temperature": 0.7}
KILL = getattr(signal, "SIGKILL", signal.SIGTERM)  # Windows has no SIGKILL, and SIGTERM stops a process there.


class Bank:
    """A pretend bank: a file with one line for each payment. It's the real system in this chapter."""

    def __init__(self, folder):
        self.path = Path(folder) / "bank.jsonl"

    def pay(self, order):
        with self.path.open("a") as file:
            file.write(json.dumps({"order": order, "amount": ORDERS[order]}) + "\n")

    def payments(self):
        """Every payment, in the order it happened, repeats included."""
        if not self.path.exists():
            return []
        return [json.loads(line)["order"] for line in self.path.read_text().splitlines()]

    def paid(self, order):
        return order in self.payments()

    def unpaid(self):
        return [order for order in ORDERS if not self.paid(order)]


def refund_tools(bank, crash_after=0):
    """The job's two tools. If crash_after is 2, the process kills itself right after its second payment."""
    made = {"payments": 0}

    @tool
    def list_refunds() -> str:
        """List the orders that need a refund."""
        return "\n".join(f"{order}: {amount:.2f}" for order, amount in ORDERS.items())

    @tool
    def issue_refund(order: Annotated[str, "The order number, such as QC-101"]) -> str:
        """Refund one order. This pays real money."""
        if order not in ORDERS:
            return f"Error: no order called {order}"
        bank.pay(order)
        made["payments"] += 1
        if made["payments"] == crash_after:
            os.kill(os.getpid(), KILL)  # The worst moment: the money has gone, and nothing has been saved.
        return f"Refunded {order}."

    return list_refunds, issue_refund


def job_agent(tools, hooks=(), options=OPTIONS):
    return Agent(Retry(RescueToolCalls(load_model())), Toolbox(list(tools)), system=SYSTEM, max_steps=16,
                 options=options, hooks=list(hooks))


def job_settings():
    """Read the command line: python3 job.py [crash_after] [folder]."""
    crash_after = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    folder = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    return crash_after, folder


def one_line(text, size=100):
    """Shorten an answer to one line, because a confused model can write a lot."""
    return " ".join(text.split())[:size]
