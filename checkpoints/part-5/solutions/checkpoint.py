"""Part 5 checkpoint. Complete each TODO, then run: python3 -m pytest test_checkpoint.py"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Annotated

from whitebox import (
    Agent, Checkpoint, Memory, Plan, RescueToolCalls, Retry, Toolbox, Trim, load_messages, load_model, once, tool,
    until_done,
)

DEPOSITS = {"L-201": 5, "L-202": 12, "L-203": 8, "L-204": 20, "L-205": 15}
SYSTEM = (
    "You help the desk at Larkfield Library. Call return_deposit for each member who is owed a deposit, one at a time. "
    "When the user tells you something about themselves worth keeping, call remember. Then reply briefly."
)
TASK = f"Return the deposits for these members: {', '.join(DEPOSITS)}. Then reply DONE."
BUDGET = 3000


class Bank:
    """Provided: a pretend bank. Its file is the real record of what was paid."""

    def __init__(self, path):
        self.path = Path(path)

    def paid(self):
        return [json.loads(line)["member"] for line in self.path.read_text().splitlines()] if self.path.exists() else []

    def pay(self, member):
        with self.path.open("a") as file:
            file.write(json.dumps({"member": member}) + "\n")
            file.flush()
            os.fsync(file.fileno())


def deposit_tool(bank, crash_after=0):
    """Provided: pays one deposit. With crash_after, the process dies right after that many payments."""
    count = {"paid": 0}

    @tool
    def return_deposit(member: Annotated[str, "The member number, such as L-201"]) -> str:
        """Return one member's deposit. This pays real money."""
        if member not in DEPOSITS:
            return f"Error: no member called {member}"
        bank.pay(member)
        count["paid"] += 1
        if count["paid"] == crash_after:
            os._exit(1)
        return f"Returned {member}."

    return return_deposit


def build_agent(model, memory, tools, path):
    """TODO 1: Return an Agent for the desk. Wrap model in RescueToolCalls, then wrap that in Retry. Give it a Toolbox
    with memory.tool() and everything in tools. Put the notes in the system prompt with memory.system(SYSTEM). Use
    these hooks: memory, Trim(BUDGET) and Checkpoint(path). Use max_steps 16 and the option temperature 0.7.
    """
    return Agent(
        Retry(RescueToolCalls(model)),
        Toolbox([memory.tool(), *tools]),
        system=memory.system(SYSTEM),
        max_steps=16,
        options={"temperature": 0.7},
        hooks=[memory, Trim(BUDGET), Checkpoint(path)],
    )


def safe_tool(deposit, bank):
    """TODO 2: Return deposit made safe to repeat with once, by asking the bank whether this member was paid."""
    return once(deposit, lambda member: member in bank.paid())


def left_to_pay(bank):
    """TODO 3: Return the member numbers in DEPOSITS that the bank hasn't paid, in order."""
    paid = bank.paid()
    return [member for member in DEPOSITS if member not in paid]


def finish(agent, bank, path):
    """TODO 4: Load any saved messages from path, then use until_done to run agent until left_to_pay is empty.
    For the request, use: f"These members still need return_deposit: {', '.join(items)}. Then reply DONE."
    """
    return until_done(
        agent,
        lambda: left_to_pay(bank),
        lambda items: f"These members still need return_deposit: {', '.join(items)}. Then reply DONE.",
        load_messages(path),
    )


def build_planner(model, index):
    """TODO 5: Return a Plan that uses model and index, finds 3 hits, and has the option temperature 0.7."""
    return Plan(model, index, 3, {"temperature": 0.7})


def job(folder, crash_after):
    """Provided: one attempt at the job, as its own process, so a crash really ends it."""
    folder = Path(folder)
    bank = Bank(folder / "bank.jsonl")
    deposit = safe_tool(deposit_tool(bank, crash_after), bank)
    agent = build_agent(load_model(), Memory(folder / "notes.json"), [deposit], folder / "run.json")
    finish(agent, bank, folder / "run.json")


def main():
    """Provided: crash the job right after a payment, start it again, then read the bank."""
    clean = 0
    for crash_after in (1, 2, 3, 4, 4):
        with tempfile.TemporaryDirectory() as folder:
            for attempt in (crash_after, 0):
                try:
                    subprocess.run([sys.executable, __file__, folder, str(attempt)], capture_output=True, timeout=180)
                except subprocess.TimeoutExpired:
                    print("An attempt hit the 180 second limit.")
            paid = Bank(Path(folder) / "bank.jsonl").paid()
            repeats, unpaid = len(paid) - len(set(paid)), len(set(DEPOSITS) - set(paid))
            clean += not repeats and not unpaid
            print(f"crash after {crash_after}: {len(paid)} payments, {repeats} repeats, {unpaid} unpaid")
    print(f"{clean} of 5 clean")


if __name__ == "__main__":
    job(sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else main()
