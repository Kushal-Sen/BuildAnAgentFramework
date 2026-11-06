"""Ask for a plan, and search for nothing yet. One model call for each question."""
from hop_setups import OPTIONS, handbook_index
from whitebox import Plan, load_model

QUESTIONS = [
    "I'm a shift lead. How much notice must I give when I resign?",
    "I'm opening the Harbour branch on a Monday. What time do I need to arrive?",
]

planner = Plan(load_model(), handbook_index(), options=OPTIONS)

for question in QUESTIONS:
    print(question)
    for step in planner.make_plan(question):
        print("  -", step)
