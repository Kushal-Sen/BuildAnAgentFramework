"""The refund job with nothing to help it. Run it again, and it starts from the top."""
from refunds import TASK, Bank, job_agent, job_settings, one_line, refund_tools

crash_after, folder = job_settings()
agent = job_agent(refund_tools(Bank(folder), crash_after))
result = agent.run(TASK)
print(one_line(result.answer))
