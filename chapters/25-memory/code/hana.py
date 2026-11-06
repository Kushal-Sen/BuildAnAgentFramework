"""Provided: one person and her chat. Every script in this chapter uses them, so the results can be compared."""
from whitebox import Message

OPTIONS = {"temperature": 0.7}
SYSTEM = "You are the Quillon Coffee staff assistant. Answer from what you're told about this person."
REMEMBER_SYSTEM = ("You are the Quillon Coffee staff assistant. When the user tells you something about themselves "
                   "that's worth keeping for later, call remember with it. Then reply briefly.")

# name: what Hana says, the question for a later session, and the words a right answer must contain.
FACTS = [
    ("surname", "Hi, I'm Hana Kowalski, I've just joined the Old Mill branch.", "What's my surname?", "kowalski"),
    ("staff", "My staff number is 5093.", "What's my staff number?", "5093"),
    ("locker", "My locker is number 212.", "What's my locker number?", "212"),
    ("day", "Can't do Thursdays, I've got a night class in bookkeeping.", "Which day can't I work?", "thursday"),
    ("knee", "What's the rule on sick pay? I've got a bad knee so I might need it.", "What health problem do I have?", "knee"),
    ("allergy", "Does the syrup shelf get wiped down? I'm allergic to hazelnuts.", "What am I allergic to?", "hazelnut"),
    ("contact", "Emergency contact is my brother Piotr.", "Who is my emergency contact?", "piotr"),
    ("trip", "Can I carry leave over? I'm saving days for a trip to Lisbon in October.", "Where am I going in October?", "lisbon"),
    ("rota", "Been on the 06:15 opener rota since Monday.", "What time is my opener rota?", "06:15"),
    ("badge", "My badge says Johanna but everyone calls me Hana.", "What name is on my badge?", "johanna"),
    ("bus", "I get the number 18 bus in, so Sundays are tight for me.", "Which bus do I take?", "18"),
    ("hygiene", "My food hygiene certificate runs out on 9 November.", "When does my food hygiene certificate run out?", "9 november"),
]

# Everything else she says. Some of it sounds like a fact, but none of it is about her.
OTHER = [
    "What time does Old Mill open on a Sunday?", "How do I report a broken grinder?", "Thanks, that's useful!",
    "A customer left a blue scarf on table 4, what do I do with it?", "Do we share tips?",
    "Can you write a short note asking to swap my Saturday?", "The oat milk delivery came two hours late today.",
    "How much notice do I give if I resign?", "Someone asked if the flapjack has nuts in it.", "ok cool",
    "Which form do I use for a burn at work?", "How many stamps for a free drink?",
    "Harbour was packed when I dropped in earlier.", "Are trainers allowed with the uniform?",
    "Who do I ask for a reference?", "Does the staff discount work on bags of beans?",
    "What's the difference between Band B and Band C?", "Can you go through the closing checklist?",
    "Marek on the next till is off with flu.", "Where do I find next week's rota?",
    "How do I clean the steam wand?", "One more thing, how do I log waste?",
    "Do we charge extra for oat milk?", "Got it, cheers.",
]


def chat():
    """All 36 messages, with a fact before every second other message."""
    messages = []
    for index, other in enumerate(OTHER):
        if index % 2 == 0:
            messages.append(FACTS[index // 2][1])
        messages.append(other)
    return messages


def with_notes(notes):
    """The system prompt for a new session, with these notes in it."""
    return SYSTEM + "\n\nThings this person told you before:\n" + "\n".join(f"- {note}" for note in notes)


def recall(model, system):
    """A new session for each fact: nothing but the system prompt, then the question. Returns name: answer."""
    return {name: model.chat([Message("system", system), Message("user", question)], **OPTIONS).content
            for name, _, question, _ in FACTS}


def right(answers):
    """The names of the facts answered correctly."""
    return [name for name, _, _, word in FACTS if word in answers[name].lower()]


def about_hana(note):
    """True if this note holds one of the 12 facts."""
    return any(word in note.lower() for _, _, _, word in FACTS)
