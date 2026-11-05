"""Chapter 17 exercises. Complete each TODO, then run: python3 -m pytest test_exercises.py"""
import time
from dataclasses import replace

from whitebox import Agent, Hook, LoopGuard, Model, RescueToolCalls, Retry
from whitebox.reliability import rescue


class CountingModel(Model):
    """TODO 1: Wrap a model and count its calls. __init__ is done for you.
    Write chat: add 1 to self.calls, then pass everything on to the wrapped model.
    """

    def __init__(self, model):
        self.model = model
        self.calls = 0


class CappedRetry(Retry):
    """TODO 2: A Retry whose wait never goes above max_delay. __init__ is done for you.
    Override wait_or_raise. It works like Retry's, but the wait is capped with min().
    """

    def __init__(self, model, max_delay, **settings):
        super().__init__(model, **settings)
        self.max_delay = max_delay


def rescue_with_words(reply, tools):
    """TODO 3: rescue() only handles replies that are nothing but a tool call. Handle a tool
    call with words around it, such as: Sure! {"name": "ping", "arguments": {}} Hope that helps.

    Slice from the first { to the last } in reply.content. Use replace() to make a copy of the
    reply with that content, and pass the copy to rescue(). If the result has tool calls, return
    it. Otherwise return the original reply, with its words intact. str.find and str.rfind give
    -1 when they find nothing, and then you should also return the original reply.
    """
    return reply


class ToolBudget(Hook):
    """TODO 4: Allow at most limit tool calls in a run, whatever the tools or arguments.
    In before_tool, count the call. Past the limit, return text that starts with "Error: ".
    In on_finish, reset the count, so the next run starts fresh.
    """

    def __init__(self, limit):
        self.limit = limit
        self.used = 0


def safe_agent(model, toolbox, sleep=time.sleep):
    """TODO 5: Return an Agent with these safety nets: model wrapped in RescueToolCalls, that
    wrapped in Retry (pass sleep=sleep), and a LoopGuard hook.
    """
    return None
