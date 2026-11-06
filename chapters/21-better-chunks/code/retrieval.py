"""Measure retrieval alone, with no chat model: python3 retrieval.py NAME NAME ..."""
import sys

from library import all_documents, build_index, text_found
from questions import HANDBOOK, RECORDS, file_cases
from whitebox import hit_rate

documents = all_documents()
rows = [row for row in HANDBOOK + RECORDS if row[4]]
single = [row for row in rows if row[1] != "hop"]  # A hop's answer needs two files.

SETUPS = {
    "plain60": lambda: build_index(documents, 60),
    "titles60": lambda: build_index(documents, 60, titles=True),
    "plain120": lambda: build_index(documents, 120),
    "titles120": lambda: build_index(documents, 120, titles=True),
}

print(f"{'':<12} {'File hit, of ' + str(len(rows)):<18} {'Text found, of ' + str(len(single)):<16}")
print(f"{'Setup':<12} {'k=1':>4} {'k=3':>4} {'k=5':>4}     {'k=1':>4} {'k=3':>4} {'k=5':>4}")
for label in sys.argv[1:]:
    index = SETUPS[label]()
    file_hits = [hit_rate(index, file_cases(rows), k)[0] for k in (1, 3, 5)]
    texts = [text_found(index, single, k)[0] for k in (1, 3, 5)]
    print(f"{label:<12} {file_hits[0]:>4} {file_hits[1]:>4} {file_hits[2]:>4}     {texts[0]:>4} {texts[1]:>4} {texts[2]:>4}")
