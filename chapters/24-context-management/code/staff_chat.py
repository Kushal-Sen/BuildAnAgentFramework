"""Provided: the long staff chats this chapter tests. A person tells the assistant a few facts, then asks handbook questions."""
from pathlib import Path

from whitebox import Message

SYSTEM = "You are the Quillon Coffee staff assistant. End every reply with the word Cheers."

# Three facts, told at the very start of the chat, and how to ask for each one back.
PLANTED = [
    ("Hi, I'm Priya and I work at the Harbour branch.", "Hello Priya, good to meet you. Cheers"),
    ("My staff number is 4471.", "Thanks, I've noted staff number 4471. Cheers"),
    ("I can't work Tuesdays because of my college course.", "Understood, no Tuesdays. Cheers"),
]
QUESTIONS = [
    ("name", "What's my name?", "priya"),
    ("number", "What's my staff number?", "4471"),
    ("day", "Which day can't I work?", "tuesday"),
]

# Two more facts for the 45-turn chat: one near the middle, and one in the last turn.
MIDDLE = ("My manager is called Tomasz.", "Noted, your manager is Tomasz. Cheers")
RECENT = ("My shift tomorrow starts at 06:30.", "Got it, 06:30 tomorrow. Cheers")
FIVE_QUESTIONS = QUESTIONS + [
    ("manager", "What's my manager called?", "tomasz"),
    ("shift", "What time does my shift start tomorrow?", "06:30"),
]

# Twelve facts, spread across a 120-turn chat: what you say, how to ask, and the word the answer must have.
FACTS = [
    ("name", "Hi, I'm Priya Nair from the Harbour branch.", "What's my surname?", "nair"),
    ("number", "My staff number is 4471.", "What's my staff number?", "4471"),
    ("day", "I can't work Tuesdays because of my college course.", "Which day can't I work?", "tuesday"),
    ("locker", "My locker is number 212.", "What's my locker number?", "212"),
    ("allergy", "I'm allergic to cashews, so I don't handle the cashew syrup.", "What am I allergic to?", "cashew"),
    ("manager", "My manager is called Tomasz.", "What's my manager called?", "tomasz"),
    ("bus", "My bus gets in at 07:52 on weekdays.", "What time does my bus get in?", "07:52"),
    ("size", "My uniform order was a size 10 apron.", "What size apron did I order?", "10"),
    ("till", "I was trained on till three last week.", "Which till was I trained on?", "three"),
    ("sister", "My sister Anjali also works here, at Old Mill.", "What's my sister called?", "anjali"),
    ("course", "My food safety course expires on 14 March.", "When does my food safety course expire?", "14 march"),
    ("shift", "My shift tomorrow starts at 06:30.", "What time does my shift start tomorrow?", "06:30"),
]


def filler(count):
    """Handbook turns: a question, and the first 130 words of a handbook file as the answer."""
    files = sorted(Path("workspace/handbook").glob("*.md"))
    turns = []
    for number in range(count):
        file = files[number % len(files)]
        words = " ".join(file.read_text().split()[:130])
        turns.append((f"What does the handbook say about {file.stem.replace('-', ' ')}?", words + " Cheers"))
    return turns


def to_messages(turns):
    """Turn (question, answer) pairs into a chat, with the system message first."""
    messages = [Message("system", SYSTEM)]
    for question, answer in turns:
        messages += [Message("user", question), Message("assistant", answer)]
    return messages


def staff_chat(handbook_turns):
    """The three planted facts, then this many handbook turns."""
    return to_messages(PLANTED + filler(handbook_turns))


def five_fact_chat():
    """45 turns: three facts at the start, one near the middle, and one at the very end."""
    turns = filler(40)
    return to_messages(PLANTED + turns[:18] + [MIDDLE] + turns[18:] + [RECENT])


def long_turns(total=120):
    """120 turns, with the twelve facts spread evenly among the handbook questions."""
    turns = filler(total - len(FACTS))
    gap = len(turns) // (len(FACTS) - 1)
    result = []
    for index, (_, statement, _, _) in enumerate(FACTS):
        result.append((statement, "Noted. Cheers"))
        result += turns[index * gap:(index + 1) * gap]
    return result[:total]
