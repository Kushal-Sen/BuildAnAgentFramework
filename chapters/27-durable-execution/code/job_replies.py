"""The job with no crash, printing what each model reply asked for."""
import tempfile
from collections import Counter

from refunds import TASK, Bank, job_agent, one_line, refund_tools
from whitebox import Hook


class Replies(Hook):
    """Note what each reply asked for, as one short piece of text."""

    def __init__(self):
        self.seen = []

    def after_model(self, reply):
        counts = Counter(call.name for call in reply.tool_calls)
        asked = [f"{count} {name}" for name, count in counts.items()]
        self.seen.append(" + ".join(asked) or one_line(reply.content, 20))


with tempfile.TemporaryDirectory() as folder:
    bank = Bank(folder)
    replies = Replies()
    job_agent(refund_tools(bank), [replies]).run(TASK)
    print(" | ".join(replies.seen), f"| bank: {len(bank.payments())} payments, {len(bank.unpaid())} unpaid")
