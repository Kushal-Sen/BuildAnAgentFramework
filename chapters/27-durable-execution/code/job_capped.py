"""The finished job with a very low cap on each reply, to see what a cap does when it bites."""
from refunds import OPTIONS, Bank, job_agent, job_settings, one_line, refund_tools
from whitebox import Checkpoint, Hook, load_messages, once, until_done

CAP = 60  # Far too low on purpose. A sensible cap would leave room for a whole batch.


class ReplySizes(Hook):
    def after_model(self, reply):
        print(f"reply: {len(reply.tool_calls)} calls, {reply.tokens_out} tokens")


def still_to_do(orders):
    return f"The bank shows these orders still need issue_refund: {', '.join(orders)}. Call it for each, then reply DONE."


crash_after, folder = job_settings()
state = folder / "state.json"
bank = Bank(folder)
list_refunds, issue_refund = refund_tools(bank, crash_after)
agent = job_agent([list_refunds, once(issue_refund, bank.paid)], [Checkpoint(state), ReplySizes()],
                  {**OPTIONS, "num_predict": CAP})
result = until_done(agent, bank.unpaid, still_to_do, load_messages(state))
print(one_line(result.answer) if result else "Nothing to do.")
print("Still unpaid:", bank.unpaid() or "nothing")
