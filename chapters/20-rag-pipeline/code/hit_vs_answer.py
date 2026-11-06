"""Compare the file hit with the answers. Reads the two rag60 reports that eval_all.py saved."""
from library import all_documents, build_index
from questions import HANDBOOK, RECORDS
from whitebox import hit_rate
from whitebox.evals import load_report

index = build_index(all_documents(), 60)
reports = [load_report("rag60.json"), load_report("rag60-again.json")]
passed = {}
for report in reports:
    for row in report.rows:
        passed[row.name] = passed.get(row.name, 0) + row.passed

print(f"{'Question':<24} {'File hit':<9} Passed")
for name, kind, question, answers, files in HANDBOOK + RECORDS:
    if not files:
        continue
    hit = hit_rate(index, [(question, files)], 5)[0] == 1
    score = passed[f"{kind}:{name}"]
    if hit != (score == 6):  # Only print the questions where the two disagree.
        print(f"{name:<24} {'yes' if hit else 'no':<9} {score}/6")
