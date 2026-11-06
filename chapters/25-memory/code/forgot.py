"""Tell the agent three things, then ask in the same session and in a new one."""
from hana import OPTIONS, SYSTEM
from whitebox import Agent, load_model

TOLD = ["Hi, I'm Hana Kowalski, I've just joined the Old Mill branch.", "My locker is number 212.",
        "Can't do Thursdays, I've got a night class in bookkeeping."]
QUESTION = "What's my locker number?"
RUNS = 5

agent = Agent(load_model(), system=SYSTEM, options=OPTIONS)


def told_it():
    """Session one: each message goes in with the history so far."""
    history = None
    for text in TOLD:
        history = agent.run(text, history).messages
    return history


history = told_it()
print("Same session:", agent.run(QUESTION, history).answer)
print("New session: ", agent.run(QUESTION).answer)

same = sum("212" in agent.run(QUESTION, told_it()).answer for _ in range(RUNS))
new = sum("212" in agent.run(QUESTION).answer for _ in range(RUNS))
print(f"Over {RUNS} runs: same session {same}/{RUNS}, new session {new}/{RUNS}")
