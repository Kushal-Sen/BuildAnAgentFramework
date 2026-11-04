"""Provided, not part of the lesson: how we counted the results in this chapter.

Each check runs five times at temperature 0.7, with a different seed each time.
"""
import contextlib
import io
import json

import by_hand
from by_hand import REQUEST, SYSTEM, ask

RUNS = range(5)


def seeded(seed, log):
    """Make a chat function that uses this seed, and logs each reply."""
    def run(messages, format=None, **options):
        reply = by_hand.chat(messages, format=format, temperature=0.7, seed=seed)
        log.append(reply)
        return reply
    return run


def one_step(question, format):
    """Ask for a tool once, without running it."""
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    return [seeded(seed, [])(messages, format=format) for seed in RUNS]


def is_json(text):
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


def round_trips(question):
    """Run the whole round trip five times, and print what happened."""
    for seed in RUNS:
        log = []
        with contextlib.redirect_stdout(io.StringIO()):
            answer = ask(question, chat=seeded(seed, log))
        print(f"  {log[0]} -> {answer!r}")


question = "What was the coffee revenue on Monday?"
print("1. No schema")
replies = one_step(question, None)
print(f"  Valid JSON: {sum(map(is_json, replies))}/5")
print(f"  A reply: {replies[0]!r}")

print("2. With the schema")
replies = one_step(question, REQUEST)
print(f"  Valid JSON: {sum(map(is_json, replies))}/5")

print("3. A file that's there")
round_trips(question)

print("4. A file that isn't there")
round_trips("What was the coffee revenue on Sunday?")

print("5. A question that needs no tool")
round_trips("Tell me a joke.")

print("6. No tool fits, with the enum")
print(*(f"  {reply}" for reply in one_step("What's the weather in Kolkata?", REQUEST)), sep="\n")

print("7. No tool fits, without the enum")
loose = {**REQUEST, "properties": {**REQUEST["properties"], "tool": {"type": "string"}}}
print(*(f"  {reply}" for reply in one_step("What's the weather in Kolkata?", loose)), sep="\n")
