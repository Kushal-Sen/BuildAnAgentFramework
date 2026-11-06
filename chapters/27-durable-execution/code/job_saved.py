"""The job with a save before each model call, and nothing else."""
from refunds import AGAIN, TASK, Bank, job_agent, job_settings, one_line, refund_tools
from whitebox import Checkpoint, load_messages


class BeforeEachCall(Checkpoint):
    """Our first try. It saves before each model call, and does nothing after a tool."""

    def after_tool(self, call, output):
        pass


crash_after, folder = job_settings()
state = folder / "state.json"
agent = job_agent(refund_tools(Bank(folder), crash_after), [BeforeEachCall(state)])
saved = load_messages(state)
result = agent.run(AGAIN, saved) if saved else agent.run(TASK)
print(one_line(result.answer))
