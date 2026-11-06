"""Read the saved notes from who_decides.py and whole_chat.py. Reads files only, so no model is needed."""
import sys
from pathlib import Path

from hana import FACTS, about_hana, chat, right
from library import load_runs, saved

runs = load_runs("who-decides.json")
if Path(saved("whole-chat.json")).exists():
    runs += load_runs("whole-chat.json")
labels = list(dict.fromkeys(run["setup"] for run in runs))


def spread(numbers):
    return f"{min(numbers)} to {max(numbers)}"


print(f"{'Setup':<15} {'Recall':>7} {'Notes':>9} {'Unwanted':>9} {'Her words':>10}")
for label in labels:
    group = [run for run in runs if run["setup"] == label]
    recall = sum(len(right(run["answers"])) for run in group)
    notes = [len(run["notes"]) for run in group]
    extra = [sum(not about_hana(note) for note in run["notes"]) for run in group]
    kept = sum(note in chat() for run in group for note in run["notes"])
    print(f"{label:<15} {f'{recall}/{len(group) * len(FACTS)}':>7} {spread(notes):>9} {spread(extra):>9} "
          f"{f'{kept}/{sum(notes)}':>10}")

print("\nMissed, out of 5 runs each:")
for label in labels:
    group = [run for run in runs if run["setup"] == label]
    missed = {name: sum(name not in right(run["answers"]) for run in group) for name, _, _, _ in FACTS}
    print(f"{label:<15}", ", ".join(f"{name} {count}" for name, count in missed.items() if count))

# Name a setup to see its unwanted notes, such as: python3 read_notes.py "user's words"
if len(sys.argv) > 1:
    print(f"\nUnwanted notes in {sys.argv[1]}, with how many runs saved each:")
    group = [run for run in runs if run["setup"] == sys.argv[1]]
    unwanted = [note for run in group for note in run["notes"] if not about_hana(note)]
    for note in sorted(set(unwanted)):
        print(f"{unwanted.count(note)}  {note}")
