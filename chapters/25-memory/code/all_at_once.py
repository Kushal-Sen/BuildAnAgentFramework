"""Save notes the obvious way: hand the model a block of the chat, and ask it to list the facts."""
from hana import FACTS, chat
from whitebox import Message, load_model

ROUNDS = 5
BLOCK = 12  # Messages at a time, so the whole chat takes three blocks.
EXTRACT = ("Below is part of a chat. List only facts the user stated about themselves, one per line, starting "
           "with '- '. Copy names, numbers, dates and times exactly. If there are none, reply NONE.\n\n{text}")

model = load_model()
messages = chat()
blocks = [messages[start:start + BLOCK] for start in range(0, len(messages), BLOCK)]
empty = 0
for number in range(1, ROUNDS + 1):
    found = []
    for block in blocks:
        reply = model.chat([Message("user", EXTRACT.format(text="\n".join(block)))], temperature=0.2).content
        empty += reply.strip().upper().startswith("NONE")
        found += [line for line in reply.splitlines() if line.startswith("- ")]
    kept = [name for name, _, _, word in FACTS if word in " ".join(found).lower()]
    print(f"round {number}: {len(found)} lines, {len(kept)} of {len(FACTS)} facts")
print(f"NONE in {empty} of {ROUNDS * len(blocks)} blocks")
print("One round's lines:", *found, sep="\n  ")
