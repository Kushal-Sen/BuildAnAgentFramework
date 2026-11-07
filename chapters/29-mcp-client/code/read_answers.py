"""Read the saved answers from someone_elses_text.py. The score counts tool calls. What did the model say to the user?"""
import json
import textwrap

from library import load_runs

for row in load_runs("injection.json"):
    answers = [run["answer"] for run in row["details"]]
    relayed = [answer for answer in answers if "send_note" in answer or "records" in answer.lower()]
    print(f"{row['server']:<21} {row['system']:<8} called send_note {row['called_send_note']} of {row['runs']}, "
          f"passed it on {len(relayed)} of {row['runs']}")
    if relayed:
        print(textwrap.indent(textwrap.fill(" ".join(relayed[0].split()), 80), "  "))
