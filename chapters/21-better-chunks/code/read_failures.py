"""Provided: list every question that lost a run, with what each measure says about it.

Reads two saved reports from eval_setup.py: python3 read_failures.py titles60 titles60-again
"""
import sys

from library import all_documents, build_index, holds_answer, saved
from questions import HANDBOOK, RECORDS
from whitebox.evals import load_report

reports = [load_report(saved(f"{label}.json")) for label in sys.argv[1:]]
passed, runs = {}, {}
for report in reports:
    for row in report.rows:
        passed[row.name] = passed.get(row.name, 0) + row.passed
        runs[row.name] = runs.get(row.name, 0) + row.runs

index = build_index(all_documents(), 60, titles=True)
print(f"{'Question':<18} {'Kind':<8} {'File hit':<9} {'Text found':<11} Passed")
for row in HANDBOOK + RECORDS:
    name, kind, question, answers, files = row
    key = f"{kind}:{name}"
    if passed[key] == runs[key]:
        continue
    hits = index.search(question, 5)
    sources = {hit.source for hit in hits}
    file_hit = "yes" if all(file in sources for file in files) else "no"
    text = "-" if kind == "hop" else "yes" if any(holds_answer(hit, row) for hit in hits) else "no"
    print(f"{name:<18} {kind:<8} {file_hit:<9} {text:<11} {passed[key]}/{runs[key]}")
