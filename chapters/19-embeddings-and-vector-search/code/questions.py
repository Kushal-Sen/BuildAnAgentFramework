"""Provided: the test questions, and the file that holds each answer.

These were fixed before anything was measured. Each entry is a question and the handbook files
that count as right. Some answers are in two places, so a question can have two right files.
"""
DIRECT = [
    ("How many grams of coffee and espresso does the house blend recipe use?", ["espresso-recipe.md"]),
    ("How much is the till float?", ["cash-handling.md"]),
    ("When is payday?", ["wages.md"]),
    ("How much extra do oat, soya and coconut milk cost?", ["milk-and-alternatives.md"]),
    ("What temperature must fridges stay at?", ["food-safety.md"]),
    ("When are coffee grounds collected?", ["waste-and-recycling.md"]),
    ("What temperature must hot food reach in the centre?", ["food-safety.md"]),
    ("How many hot drinks until a customer gets a free one on the loyalty card?", ["loyalty-card.md"]),
]

# These avoid the handbook's own words.
REWORDED = [
    ("How many vacation days do I get as a full-timer?", ["annual-leave.md"]),
    ("I'm a barista and I want to quit. How much warning do I have to give?", ["resignation.md"]),
    ("I woke up feeling awful and can't make it in. How do I let my boss know?", ["sickness-absence.md"]),
    ("My dad just passed away. How much paid time can I have?", ["bereavement-leave.md"]),
    ("I found evidence of mice in the storeroom. Who handles that?", ["food-safety.md"]),
    ("I scalded my hand on the steam wand. How long should I hold it under the tap?", ["first-aid.md"]),
    ("Can I get money back for buying work footwear?", ["uniform.md"]),
    ("Do I need to do anything about my ponytail at work?", ["uniform.md"]),
]

# These ask about an exact code.
CODES = [
    ("What does E44 mean?", ["grinder-errors.md"]),
    ("The grinder shows E31. What do I do?", ["grinder-errors.md"]),
    ("What is refund reason code R5 for?", ["refunds.md"]),
    ("What is form IR-9 for?", ["forms.md", "data-protection.md"]),
    ("What is HR-15?", ["forms.md", "flexible-working.md"]),
    ("What is FN-6 used for?", ["forms.md"]),
]

# The handbook doesn't answer these at all.
NOT_IN_HANDBOOK = [
    "What percentage does Quillon match on pension contributions?",
    "Does Quillon offer dental insurance?",
    "What is the customer wifi password at Harbour?",
    "Are dogs allowed inside the Riverside branch?",
]
