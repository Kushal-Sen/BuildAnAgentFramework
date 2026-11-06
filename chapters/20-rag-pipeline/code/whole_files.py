"""Was the whole-files score fair? Give whole files room, and run all 42 questions again."""
from library import all_documents
from questions import HANDBOOK, RECORDS, summary, to_cases
from whitebox import Chunk, Index, OllamaEmbedder, Rag, load_model, run_eval

whole = Index(OllamaEmbedder())
whole.add([Chunk(text, name) for name, text in all_documents().items()])

rag = Rag(load_model(), whole, 5, {"temperature": 0.7, "num_ctx": 16384})
cases = to_cases(HANDBOOK + RECORDS)
report = run_eval(rag, cases, runs=3, label="whole 16384")
print(summary(report))

result = rag.run("How much stock was lost when the Harbour cellar flooded?")
print("tokens_in:", result.messages[-1].tokens_in)
