"""The finished job. The bank says what's left, and the bank says when it's over."""
from refunds import Bank, job_agent, job_settings, one_line, refund_tools
from whitebox import Checkpoint, load_messages, once, until_done


def still_to_do(orders):
    return f"The bank shows these orders still need issue_refund: {', '.join(orders)}. Call it for each, then reply DONE."


crash_after, folder = job_settings()
state = folder / "state.json"
bank = Bank(folder)
list_refunds, issue_refund = refund_tools(bank, crash_after)
agent = job_agent([list_refunds, once(issue_refund, bank.paid)], [Checkpoint(state)])
result = until_done(agent, bank.unpaid, still_to_do, load_messages(state))
print(one_line(result.answer) if result else "Nothing to do.")
print("Still unpaid:", bank.unpaid() or "nothing")
