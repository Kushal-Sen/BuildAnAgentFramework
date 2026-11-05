"""An agent that must ask you before it saves anything."""
from pathlib import Path
from typing import Annotated

from sales_tools import add_numbers, list_files, read_file
from whitebox import Agent, Approval, Printer, Toolbox, load_model, tool

QUESTION = "Read sales/monday.txt, then save a note with Monday's coffee revenue."
NOTE = Path(__file__).parent / "workspace" / "note.txt"


@tool
def save_note(text: Annotated[str, "The text to save"]) -> str:
    """Save a short note."""
    NOTE.write_text(text)
    return "Saved."


toolbox = Toolbox([list_files, read_file, add_numbers, save_note])
hooks = [Printer(), Approval(["save_note"])]
agent = Agent(load_model(), toolbox, options={"temperature": 0}, hooks=hooks)
print("Answer:", agent.run(QUESTION).answer)
print("Note saved:", NOTE.exists())
