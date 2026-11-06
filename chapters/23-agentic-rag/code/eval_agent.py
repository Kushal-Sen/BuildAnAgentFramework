"""Run setups on all 42 questions, three times each: python3 eval_agent.py NAME NAME ..."""
import sys

from fixes import Split
from library import OPTIONS, Keep, Remember, all_documents, build_agent, build_hybrid, build_index
from questions import HANDBOOK, RECORDS, summary, to_cases
from whitebox import Rag, load_model, run_eval

documents = all_documents()
cases = to_cases(HANDBOOK + RECORDS)
model = load_model()

SETUPS = {
    "titles60": lambda: Rag(model, build_index(documents, 60), 5, OPTIONS),
    "titles60-again": lambda: Rag(model, build_index(documents, 60), 5, OPTIONS),
    "titles120": lambda: Rag(model, build_index(documents, 120), 5, OPTIONS),
    "hybrid60": lambda: Rag(model, build_hybrid(documents, 60), 5, OPTIONS),
    "agent60": lambda: build_agent(model, Remember(build_index(documents, 60))),
    "agent60-again": lambda: build_agent(model, Remember(build_index(documents, 60))),
    "agent-hybrid60": lambda: build_agent(model, Remember(build_hybrid(documents, 60))),
    "agent-hybrid60-again": lambda: build_agent(model, Remember(build_hybrid(documents, 60))),
    "split60": lambda: Split(model, Remember(build_index(documents, 60)), 3, OPTIONS),
    "split60-again": lambda: Split(model, Remember(build_index(documents, 60)), 3, OPTIONS),
}

for label in sys.argv[1:]:
    keep = Keep(SETUPS[label]())
    report = run_eval(keep, cases, runs=3, label=label)
    print(summary(report), flush=True)
    report.save(f"{label}.json")
    keep.save(f"{label}-runs.json")
