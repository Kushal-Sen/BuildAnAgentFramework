"""Session two: a new program with no history. All it has is hana.json."""
from hana import OPTIONS, REMEMBER_SYSTEM
from whitebox import Agent, Memory, Toolbox, load_model

QUESTIONS = ["What's my locker number?", "Which day can't I work?", "Which branch am I at?"]
RUNS = 5

memory = Memory("hana.json")
print(f"Read {len(memory.notes)} notes")
agent = Agent(load_model(), Toolbox([memory.tool()]), system=memory.system(REMEMBER_SYSTEM), max_steps=4,
              options=OPTIONS, hooks=[memory])

for question in QUESTIONS:
    print(question, agent.run(question).answer)

words = {"What's my locker number?": "212", "Which day can't I work?": "thursday", "Which branch am I at?": "old mill"}
for question, word in words.items():
    good = sum(word in agent.run(question).answer.lower() for _ in range(RUNS))
    print(f"{good}/{RUNS}  {question}")
print(f"Notes now: {len(memory.notes)}")
