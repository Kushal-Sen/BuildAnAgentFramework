"""The same 43-turn chat, with CutWarning watching, at the default window and at a bigger one."""
from library import OPTIONS
from staff_chat import staff_chat
from whitebox import Agent, CutWarning, load_model

QUESTION = "What's my staff number?"

model = load_model()

for label, options in (("Default window", OPTIONS), ("num_ctx 16384", {**OPTIONS, "num_ctx": 16384})):
    print(label, flush=True)
    agent = Agent(model, options=options, hooks=[CutWarning()])
    result = agent.run(QUESTION, history=staff_chat(40))
    print("  Answer:", result.answer, flush=True)
