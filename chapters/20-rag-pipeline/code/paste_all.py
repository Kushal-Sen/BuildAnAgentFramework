"""Optional exercise: paste all 95 files, however big the context. usage: python3 paste_all.py NUM_CTX [QUESTIONS]"""
import sys
import time

from library import all_documents
from paste import Paste
from questions import HANDBOOK, RECORDS, to_case
from whitebox import ModelError, load_model

NAMES = ["float", "fridge", "e44", "pension", "flood", "film-crew", "lantern-price", "fennel-min"]
DOCUMENT_TOKENS = 69872  # Measured by count_tokens.py.

num_ctx = int(sys.argv[1])
paste = Paste(load_model(), all_documents(), {"temperature": 0.7, "num_ctx": num_ctx})
cases = [to_case(row) for row in HANDBOOK + RECORDS if row[0] in NAMES]
if len(sys.argv) > 2:
    cases = cases[:int(sys.argv[2])]

passed, answered, seconds, tokens_in = 0, 0, 0, 0
for case in cases:
    start = time.time()
    try:
        result = paste.run(case.question)
    except ModelError as error:
        print(f"{case.name:<22} no answer: {error}", flush=True)
        continue
    seconds += time.time() - start
    answered += 1
    ok = all(check.test(result) for check in case.checks)
    passed += ok
    tokens_in = result.messages[-1].tokens_in
    print(f"{case.name:<22} {'pass' if ok else 'FAIL'}  {result.answer[:60]!r}", flush=True)

print(f"\nnum_ctx {num_ctx}: {passed}/{len(cases)} passed, {seconds / max(answered, 1):.0f} seconds per question")
print(f"tokens_in {tokens_in:,} of {DOCUMENT_TOKENS:,} ({tokens_in / DOCUMENT_TOKENS:.0%} of the text)")
