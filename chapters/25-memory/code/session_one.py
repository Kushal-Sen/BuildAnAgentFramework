"""Session one: a short chat with an agent that has Memory. The notes go into hana.json."""
from hana import OPTIONS, REMEMBER_SYSTEM
from whitebox import Agent, Memory, Toolbox, load_model

CHAT = ["Hi, I'm Hana Kowalski, I've just joined the Old Mill branch.", "How do I report a broken grinder?",
        "My locker is number 212.", "Can't do Thursdays, I've got a night class in bookkeeping.",
        "The oat milk delivery came two hours late today.", "Thanks, that's useful!"]

memory = Memory("hana.json")
agent = Agent(load_model(), Toolbox([memory.tool()]), system=memory.system(REMEMBER_SYSTEM), max_steps=4,
              options=OPTIONS, hooks=[memory])

history = None
for text in CHAT:
    result = agent.run(text, history)
    history = result.messages
    print(f"{len(memory.notes)} notes after: {text}")
