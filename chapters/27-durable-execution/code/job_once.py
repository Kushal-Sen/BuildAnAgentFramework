"""The job with Checkpoint, and a payment tool that asks the bank first."""
from refunds import AGAIN, TASK, Bank, job_agent, job_settings, one_line, refund_tools
from whitebox import Checkpoint, load_messages, once

crash_after, folder = job_settings()
state = folder / "state.json"
bank = Bank(folder)
list_refunds, issue_refund = refund_tools(bank, crash_after)
agent = job_agent([list_refunds, once(issue_refund, bank.paid)], [Checkpoint(state)])
saved = load_messages(state)
result = agent.run(AGAIN, saved) if saved else agent.run(TASK)
print(one_line(result.answer))
