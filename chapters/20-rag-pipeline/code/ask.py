"""Ask one question through the whole pipeline, and show what it found."""
from library import all_documents, build_index
from questions import HANDBOOK, RECORDS, to_case
from whitebox import Rag, load_model, run_eval

QUESTION = "How much stock was lost when the Harbour cellar flooded?"

index = build_index(all_documents(), 60)
rag = Rag(load_model(), index, k=5, options={"temperature": 0.7})

for hit in index.search(QUESTION, 5):
    print(f"{hit.score:.2f}  {hit.source}")

result = rag.run(QUESTION)
print("Answer:", result.answer)
print("tokens_in:", result.messages[-1].tokens_in)

cases = [to_case(row) for row in RECORDS + HANDBOOK if row[0] in ("flood", "dental")]
print(run_eval(rag, cases, runs=5, label="five runs each").table())
