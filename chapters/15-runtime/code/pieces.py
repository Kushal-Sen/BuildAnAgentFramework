"""Provided: watch one reply arrive piece by piece. A | marks where each piece ends."""
from whitebox import Message, load_model

model = load_model()
messages = [Message("user", "Explain what a sales report is, in two sentences.")]
for piece in model.stream(messages, temperature=0):
    if isinstance(piece, Message):
        print("\nThe last thing yielded is the whole Message:")
        print(piece)
    else:
        print(piece, end="|", flush=True)
