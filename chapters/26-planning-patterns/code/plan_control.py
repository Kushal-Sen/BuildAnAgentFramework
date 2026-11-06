"""The same four setups on questions that need no plan: 8 direct, 4 unanswerable, three runs each."""
import json

from hop_setups import CONTROLS, Counted, build_setups, handbook_index
from questions import says
from whitebox import Retry, load_model

RUNS = 3

model = Counted(Retry(load_model()))
setups = build_setups(model, handbook_index())
saved_runs = []

for label, setup in setups.items():
    print(label, flush=True)
    for name, kind, question, answers, _ in CONTROLS:
        for _ in range(RUNS):
            before = model.calls
            answer = setup.run(question).answer
            good = says(answer, answers) if answers else "don't know" in answer.lower().replace("’", "'")
            saved_runs.append({"setup": label, "name": name, "kind": kind, "answer": answer, "good": good,
                               "calls": model.calls - before})
    with open("plan-control.json", "w") as file:
        json.dump(saved_runs, file, indent=1)
print("Saved plan-control.json")
