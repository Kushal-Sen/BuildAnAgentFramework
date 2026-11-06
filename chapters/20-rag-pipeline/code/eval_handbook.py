"""Pasting against the pipeline, on the handbook only: 32 questions, three times each."""
from library import build_index
from paste import Paste
from questions import HANDBOOK, summary, to_cases
from whitebox import Rag, load_documents, load_model, run_eval

documents = load_documents("workspace/handbook")
cases = to_cases(HANDBOOK)
model = load_model()
options = {"temperature": 0.7}

setups = {
    "paste default": Paste(model, documents, options),
    "paste 8192": Paste(model, documents, {**options, "num_ctx": 8192}),
    "rag60": Rag(model, build_index(documents, 60), 5, options),
}
for label, setup in setups.items():
    report = run_eval(setup, cases, runs=3, label=label)
    print(summary(report), flush=True)
    report.save(f"handbook-{label.replace(' ', '-')}.json")
