"""The job with the finished Checkpoint, which also saves after each tool."""
from refunds import AGAIN, TASK, Bank, job_agent, job_settings, one_line, refund_tools
from whitebox import Checkpoint, load_messages

crash_after, folder = job_settings()
state = folder / "state.json"
agent = job_agent(refund_tools(Bank(folder), crash_after), [Checkpoint(state)])
saved = load_messages(state)
result = agent.run(AGAIN, saved) if saved else agent.run(TASK)
print(one_line(result.answer))
