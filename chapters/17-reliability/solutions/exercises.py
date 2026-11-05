"""Chapter 17 worked answers."""
import time
from dataclasses import replace

from whitebox import Agent, Hook, LoopGuard, Model, RescueToolCalls, Retry
from whitebox.reliability import rescue


class CountingModel(Model):
    def __init__(self, model):
        self.model = model
        self.calls = 0

    def chat(self, messages, tools=None, **options):
        self.calls += 1
        return self.model.chat(messages, tools, **options)


class CappedRetry(Retry):
    def __init__(self, model, max_delay, **settings):
        super().__init__(model, **settings)
        self.max_delay = max_delay

    def wait_or_raise(self, error, attempt):
        if not error.retryable or attempt == self.attempts:
            raise error
        self.sleep(min(self.delay * 2 ** (attempt - 1), self.max_delay))


def rescue_with_words(reply, tools):
    start = reply.content.find("{")
    end = reply.content.rfind("}")
    if start == -1 or end == -1:
        return reply
    rescued = rescue(replace(reply, content=reply.content[start:end + 1]), tools)
    return rescued if rescued.tool_calls else reply


class ToolBudget(Hook):
    def __init__(self, limit):
        self.limit = limit
        self.used = 0

    def before_tool(self, call):
        self.used += 1
        if self.used > self.limit:
            return f"Error: you've used all {self.limit} tool calls. Answer with what you have."
        return None

    def on_finish(self, result):
        self.used = 0


def safe_agent(model, toolbox, sleep=time.sleep):
    wrapped = Retry(RescueToolCalls(model), sleep=sleep)
    return Agent(wrapped, toolbox, hooks=[LoopGuard()])
