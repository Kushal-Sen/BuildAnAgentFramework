"""Provided: the agent this chapter's first scripts share, so each comparison changes only the tools."""
from library import OPTIONS
from whitebox import Agent, LoopGuard, RescueToolCalls, Retry, Toolbox

STAFF_SYSTEM = (
    "You help Quillon Coffee staff. Use the tools to find facts, and never answer from memory. "
    "If the tools can't tell you, say exactly: I don't know."
)
QUESTION = "My staff number is 1042. When is my next shift?"


def staff_agent(model, tools):
    return Agent(Retry(RescueToolCalls(model)), Toolbox(tools), system=STAFF_SYSTEM, options=OPTIONS, hooks=[LoopGuard()])


def tools_called(result):
    """The name of every tool the agent called, in order."""
    return [call.name for message in result.messages for call in message.tool_calls]


def ask(agent, question, says, runs=5):
    """Ask several times. Print what the agent called and said, and count the answers holding the text in says."""
    right = 0
    for run in range(1, runs + 1):
        result = agent.run(question)
        right += says in result.answer
        print(f"{run}. called {tools_called(result) or 'nothing'}")
        print(f"   {' '.join(result.answer.split())[:80]}")
    print(f"Says {says!r}: {right} of {runs}")
