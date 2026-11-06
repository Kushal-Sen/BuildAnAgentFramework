"""The right file, and the wrong answer. Look at what the model was given."""
from library import all_documents, build_index
from questions import RECORDS, to_case
from whitebox import Rag, load_model, run_eval

QUESTION = "How much is a Tidewater call-out?"

index = build_index(all_documents(), 60)
for hit in index.search(QUESTION, 5):
    if "£85" in hit.text:
        print(f"{hit.score:.2f} {hit.source}")
        print(hit.text.replace("\n\n", "\n"))  # Blank lines are removed, to keep this short.
        print("Does this chunk say Tidewater?", "Tidewater" in hit.text)

rag = Rag(load_model(), index, 5, {"temperature": 0.7})
case = to_case(next(row for row in RECORDS if row[0] == "tidewater-fee"))
print(run_eval(rag, [case], runs=5, label="five runs").table())
