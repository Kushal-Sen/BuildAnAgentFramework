"""Four setups on the six hop questions, five runs each: python3 plan_test.py, or python3 plan_test.py again"""
import json
import sys

from hop_setups import Counted, HOPS, build_setups, files_seen, handbook_index, what_it_did
from questions import says, strict_pass
from whitebox import Retry, load_model

RUNS = 5
SAVE_TO = "plan-test-again.json" if sys.argv[1:] == ["again"] else "plan-test.json"

model = Counted(Retry(load_model()))
setups = build_setups(model, handbook_index())
saved_runs = []

for label, setup in setups.items():
    print(label, flush=True)
    for name, _, question, answers, files in HOPS:
        for _ in range(RUNS):
            before = model.calls
            result = setup.run(question)
            queries, seen = what_it_did(result)
            saved_runs.append({
                "setup": label, "name": name, "answer": result.answer, "calls": model.calls - before,
                "loose": says(result.answer, answers),
                "strict": strict_pass(result.answer, name),
                "both_files": set(files) <= set(files_seen(seen)),
                "queries": queries, "files": files_seen(seen),
                "plan": getattr(result, "plan", None),
                "notes": result.messages[-2].content.partition("Notes from the search:\n")[2].partition("\n\nQuestion:")[0],
            })
    with open(SAVE_TO, "w") as file:  # Saved after each setup, so a stop loses only one.
        json.dump(saved_runs, file, indent=1)
print("Saved", SAVE_TO)
