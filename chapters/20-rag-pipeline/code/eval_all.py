"""Run the pipeline on all 42 questions, three times each. The whole-files row is for comparison."""
from library import all_documents, build_index
from questions import HANDBOOK, RECORDS, summary, to_cases
from whitebox import Chunk, Index, OllamaEmbedder, Rag, load_model, run_eval

documents = all_documents()
cases = to_cases(HANDBOOK + RECORDS)
model = load_model()
options = {"temperature": 0.7}

whole = Index(OllamaEmbedder())
whole.add([Chunk(text, name) for name, text in documents.items()])
size60 = build_index(documents, 60)
size120 = build_index(documents, 120)

indexes = {"rag60": size60, "rag60 again": size60, "rag120": size120, "whole files": whole}
for label, index in indexes.items():
    report = run_eval(Rag(model, index, 5, options), cases, runs=3, label=label)
    print(summary(report), flush=True)
    report.save(f"{label.replace(' ', '-')}.json")
