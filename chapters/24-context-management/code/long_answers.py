"""Print every saved answer for one fact, cut at 120 characters. Name a fact: python3 long_answers.py allergy"""
import sys

from long_scores import SETUPS, load

fact = sys.argv[1]
for label in SETUPS:
    for run in load(label):
        row = next(row for row in run["rows"] if row["name"] == fact)
        answer = row["answer"].replace("\n", " ")
        print(f"{label:<10} {'pass' if row['right'] else 'FAIL'}  {answer[:120]}")
