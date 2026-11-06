"""Ask the same question at the start of a chat, and again 40 turns later."""
from library import OPTIONS
from staff_chat import staff_chat
from whitebox import Message, load_model

QUESTION = "What's my staff number?"

model = load_model()

for handbook_turns in (0, 40):
    messages = staff_chat(handbook_turns) + [Message("user", QUESTION)]
    reply = model.chat(messages, **OPTIONS)
    print(f"After {handbook_turns + 3} turns, {len(messages)} messages sent")
    print(f"  tokens_in: {reply.tokens_in}")
    print(f"  Answer: {reply.content}")
