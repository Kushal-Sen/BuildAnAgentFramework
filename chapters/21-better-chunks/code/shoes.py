"""Titles broke this question, with the right chunk still first. What changed?"""
from library import all_documents, build_index
from questions import HANDBOOK, to_case
from whitebox import Rag, load_model, run_eval

QUESTION = "Can I get money back for buying work footwear?"

documents = all_documents()
case = to_case(next(row for row in HANDBOOK if row[0] == "shoes"))
model = load_model()

for titles in (False, True):
    index = build_index(documents, 60, titles)
    print(f"titles={titles}:", ", ".join(hit.source for hit in index.search(QUESTION, 5)))
    for k in (1, 3, 5):
        report = run_eval(Rag(model, index, k, {"temperature": 0.7}), [case], runs=5, label="")
        print(f"  k={k}: {report.rows[0].passed}/5")
