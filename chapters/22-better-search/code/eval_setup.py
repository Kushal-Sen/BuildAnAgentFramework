"""Run setups on all 42 questions, three times each: python3 eval_setup.py NAME NAME ..."""
import sys

from library import Remember, all_documents, build_hybrid, build_index
from questions import HANDBOOK, RECORDS, summary, to_cases
from whitebox import Rag, Reranker, load_model, run_eval

documents = all_documents()
cases = to_cases(HANDBOOK + RECORDS)
model = load_model()

SETUPS = {
    "plain60": lambda: build_index(documents, 60),
    "plain60-again": lambda: build_index(documents, 60),
    "titles60": lambda: build_index(documents, 60, titles=True),
    "titles60-again": lambda: build_index(documents, 60, titles=True),
    "plain120": lambda: build_index(documents, 120),
    "titles120": lambda: build_index(documents, 120, titles=True),
    "titles120-again": lambda: build_index(documents, 120, titles=True),
    "hybrid-plain60": lambda: build_hybrid(documents, 60),
    "hybrid60": lambda: build_hybrid(documents, 60, titles=True),
    "rerank60": lambda: Remember(Reranker(build_index(documents, 60, titles=True), model)),
}

for label in sys.argv[1:]:
    rag = Rag(model, SETUPS[label](), 5, {"temperature": 0.7})
    report = run_eval(rag, cases, runs=3, label=label)
    print(summary(report), flush=True)
    report.save(f"{label}.json")
