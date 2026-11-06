"""The failure: the fact is indexed and the file is found, but the answer isn't."""
from library import all_documents, build_index
from questions import RECORDS, to_case
from whitebox import Rag, hit_rate, load_model, run_eval

QUESTION = "How long was the Station card reader down just before Christmas 2025?"
FILE = "log-station-2025-12.md"

index = build_index(all_documents(), 60)
rag = Rag(load_model(), index, k=5, options={"temperature": 0.7})

for hit in index.search(QUESTION, 5):
    print(f"{hit.score:.3f}  {hit.source}")
print("File hit:", hit_rate(index, [(QUESTION, [FILE])], 5))

print("Answer:", rag.run(QUESTION).answer)
case = [to_case(row) for row in RECORDS if row[0] == "card-reader"]
print(run_eval(rag, case, runs=5, label="five runs").table())
