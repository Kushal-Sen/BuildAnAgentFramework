"""Read the saved runs of one question: python3 plan_read.py lead-notice, or add a setup: ... Split"""
import sys

from hop_setups import saved_tests

name = sys.argv[1]
setup = sys.argv[2] if len(sys.argv) > 2 else "Plan"

for run in saved_tests():
    if run["name"] == name and run["setup"] == setup:
        mark = "earned" if run["strict"] and run["both_files"] else "pass" if run["strict"] else "FAIL"
        print(f"{mark}: {' '.join(run['answer'].split())[:170]}")
        for query in run["queries"]:
            print("    search:", query[:100])
