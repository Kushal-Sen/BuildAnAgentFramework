"""Read the notes the long test ended with. It needs no model."""
from long_scores import MARK, load
from whitebox import Message, estimate_tokens

for run in load("summarise"):
    note = run["system"].partition(MARK)[2]
    print(f"Run {run['run']}: one note, about {estimate_tokens(Message('system', note)):,} tokens")
    print("  Starts:", note.replace("\n", " ")[:150])
