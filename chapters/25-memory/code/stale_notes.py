"""Four facts change. Does the new session give the new answer, when the notes are in order and when they aren't?"""
import json
import random

from hana import OPTIONS, SYSTEM
from whitebox import Memory, Message, load_model

RUNS = 5
BASE = [
    ("2026-02-02", "I'm Hana Kowalski, I work at the Old Mill branch."),
    ("2026-02-02", "My staff number is 5093."),
    ("2026-02-09", "I can't do Thursdays, I've got a night class in bookkeeping."),
    ("2026-02-16", "My locker is number 212."),
    ("2026-02-20", "Emergency contact is my brother Piotr."),
    ("2026-03-02", "I'm on the 06:15 opener rota."),
    ("2026-03-05", "I'm allergic to hazelnuts."),
    ("2026-03-11", "I'm saving days for a trip to Lisbon in October."),
]
UPDATES = [
    ("2026-06-01", "I've moved to the Harbour branch now."),
    ("2026-06-08", "Thursdays are fine now, but I can't do Tuesdays."),
    ("2026-06-15", "They gave me a new locker, number 87."),
    ("2026-06-22", "I've switched to the 07:30 opener rota."),
]
# The question, the new answer and the old answer.
CHANGED = [("Which branch do I work at?", "harbour", "old mill"), ("Which day can't I work?", "tuesday", "thursday"),
           ("What's my locker number?", "87", "212"), ("What time is my opener rota?", "07:30", "06:15")]
SAME = [("What's my staff number?", "5093"), ("Who is my emergency contact?", "piotr"),
        ("What am I allergic to?", "hazelnut"), ("Where am I going in October?", "lisbon")]
CHANGED_FROM = [BASE[0], BASE[2], BASE[3], BASE[5]]  # The old note for each changed fact.
BEFORE = ("Which branch did I work at before this one?", "old mill")
NAMES = ["Marek", "Lena", "Sam", "Mei", "Ravi", "Tola"]
DRINKS = ["flat white", "chai", "oat latte", "mocha", "americano", "cortado"]
SAME_THING = ("Note A: {a}\nNote B: {b}\n\nDoes note B replace or change the information in note A, about the same "
              "thing? Reply YES or NO only.")


def diary():
    """48 harmless notes from January to May, so the list reaches 60."""
    rng = random.Random(7)
    return [(f"2026-0{1 + number % 5}-{10 + number % 18}",
             f"On shift {number + 1} I worked with {rng.choice(NAMES)} and drank a {rng.choice(DRINKS)}.")
            for number in range(48)]


def in_order(rows):
    """The prompt Memory builds: oldest first, with the dates left out."""
    memory = Memory("not-saved.json")
    memory.notes = [{"text": text, "saved": day} for day, text in sorted(rows, key=lambda row: row[0])]
    return memory.system(SYSTEM)


def newest_first(rows):
    """The list backwards, so every old note comes after the note that replaced it."""
    rows = sorted(rows, key=lambda row: row[0], reverse=True)
    return SYSTEM + "\n\nThings this person told you before:\n" + "\n".join(f"- {text}" for _, text in rows)


def shuffled(rows, seed):
    rows = random.Random(seed).sample(rows, len(rows))
    return SYSTEM + "\n\nThings this person told you before:\n" + "\n".join(f"- {text}" for _, text in rows)


def shuffled_dates(rows, seed):
    rows = random.Random(seed).sample(rows, len(rows))
    lines = "\n".join(f"- {day}: {text}" for day, text in rows)
    return f"{SYSTEM}\n\nThings this person told you before:\n{lines}\n\nIf two notes disagree, the newest date is true."


def replace_old(model):
    """Ask the model whether each update replaces each old note, and delete the ones it says yes to."""
    rows, calls, removed = list(BASE), 0, []
    for update in UPDATES:
        for row in list(rows):
            reply = model.chat([Message("user", SAME_THING.format(a=row[1], b=update[1]))], temperature=0.2).content
            calls += 1
            if reply.strip().upper().startswith("YES"):
                rows.remove(row)
                removed.append(row[1])
        rows.append(update)
    return rows, calls, removed


def ask(model, system, question):
    reply = model.chat([Message("system", system), Message("user", question)], **OPTIONS)
    return reply.content, reply.tokens_in


def measure(model, label, build):
    """Five runs. build(run) gives the system prompt, so each shuffled run has its own order."""
    row = {"setup": label, "right": 0, "stale": 0, "both": 0, "same": 0, "before": 0, "old_last": 0, "stale_old_last": 0, "answers": []}
    for run in range(RUNS):
        system = build(run)
        for (question, new, old), before, after in zip(CHANGED, CHANGED_FROM, UPDATES):
            answer, row["tokens_in"] = ask(model, system, question)
            text = answer.lower()
            stale = old in text and new not in text
            old_last = before[1] in system and system.index(before[1]) > system.index(after[1])
            row["right"] += new in text
            row["stale"] += stale
            row["both"] += old in text and new in text
            row["old_last"] += old_last
            row["stale_old_last"] += stale and old_last
            row["answers"].append([question, answer])
        for question, word in SAME:
            row["same"] += word in ask(model, system, question)[0].lower()
        answer = ask(model, system, BEFORE[0])[0]
        row["before"] += BEFORE[1] in answer.lower()
        row["answers"].append([BEFORE[0], answer])
    print(f"{label:<20} {row['right']:>2}/20 {row['stale']:>5} {row['both']:>4} {row['same']:>3}/20 {row['before']:>4}/5 "
          f"{row['stale_old_last']:>3} of {row['old_last']:>2} {row['tokens_in']:>7}", flush=True)
    return row


if __name__ == "__main__":
    model = load_model()
    twelve = BASE + UPDATES
    sixty = diary() + twelve
    kept, calls, removed = replace_old(model)
    print(f"{'Setup':<20} {'Right':>5} {'Stale':>5} {'Both':>4} {'Same':>6} {'Before':>6} {'Old last':>8} {'Tokens':>7}")
    rows = [
        measure(model, "12 in order", lambda run: in_order(twelve)),
        measure(model, "60 in order", lambda run: in_order(sixty)),
        measure(model, "60 newest first", lambda run: newest_first(sixty)),
        measure(model, "60 shuffled", lambda run: shuffled(sixty, run)),
        measure(model, "60 shuffled + dates", lambda run: shuffled_dates(sixty, run)),
        measure(model, "12 replacing old", lambda run: in_order(kept)),
    ]
    print(f"Replacing took {calls} calls and removed {len(removed)} of the 4 old notes:", *removed, sep="\n  - ")
    with open("stale-notes.json", "w") as file:
        json.dump(rows, file, indent=1)
