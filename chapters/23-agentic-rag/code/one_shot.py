"""Chapter 20's pipeline, with chapter 21's titles, on a question that depends on a second fact."""
from library import OPTIONS, all_documents, build_index
from questions import HANDBOOK, to_case
from whitebox import Rag, load_model, run_eval

QUESTION = "I'm a shift lead. How much notice must I give when I resign?"

index = build_index(all_documents(), 60)
rag = Rag(load_model(), index, k=5, options=OPTIONS)

for hit in index.search(QUESTION, 5):
    print(f"{hit.score:.2f}  {hit.source}")

print("Answer:", rag.run(QUESTION).answer)

cases = [to_case(row) for row in HANDBOOK if row[0] == "lead-notice"]
print(run_eval(rag, cases, runs=5, label="five runs").table())
