"""Can one search do it, if it brings back more? Find pay-bands.md, then try bigger values of k."""
from library import OPTIONS, Keep, all_documents, build_index
from questions import HANDBOOK, to_case
from whitebox import Rag, load_model, run_eval

QUESTION = "I'm a shift lead. How much notice must I give when I resign?"

index = build_index(all_documents(), 60)
hits = index.search(QUESTION, 934)  # All the chunks, in order.
rank = next(number for number, hit in enumerate(hits, start=1) if hit.source == "pay-bands.md")
print(f"pay-bands.md first appears at rank {rank} of {len(hits)}")

model = load_model()
cases = [to_case(row) for row in HANDBOOK if row[0] == "lead-notice"]
for k in (5, 10, 20, rank):
    keep = Keep(Rag(model, index, k, OPTIONS))
    report = run_eval(keep, cases, runs=5, label=f"k={k}")
    print(f"k={k:<4} passed {report.score()[0]}/5  tokens_in {keep.runs[0]['tokens_in']}")

for run in keep.runs:  # The five answers from the biggest k.
    print(" -", run["answer"][:110].replace("\n", " "))
