"""Where does recall break? Three planted facts, five runs each, at each length of chat."""
from library import OPTIONS
from staff_chat import QUESTIONS, staff_chat
from whitebox import Message, Retry, load_model, total_tokens

RUNS = 5
WIDE = {**OPTIONS, "num_ctx": 16384}
DECLINES = ("sorry", "don't have", "do not have", "don't know", "not sure", "can't", "cannot", "unable")

model = Retry(load_model())  # Chapter 17: a long test should survive a slow reply.
failed = []


def test(handbook_turns, options, label):
    chat = staff_chat(handbook_turns)
    scores, rule, read = [], 0, set()
    for _, question, word in QUESTIONS:
        passed = 0
        for _ in range(RUNS):
            reply = model.chat(chat + [Message("user", question)], **options)
            right = word in reply.content.lower()
            passed += right
            rule += "cheers" in reply.content.lower()
            read.add(reply.tokens_in)
            if not right:
                failed.append(reply.content)
        scores.append(passed)
    name, number, day = scores
    print(f"{label:<8} {handbook_turns + 3:>5} {total_tokens(chat):>6,} {max(read):>6,} "
          f"{name:>5} {number:>7} {day:>4} {rule:>5}/15", flush=True)


print(f"{'Window':<8} {'Turns':>5} {'Sent':>6} {'Read':>6} {'Name':>5} {'Number':>7} {'Day':>4} {'Cheers':>8}")
for handbook_turns in (0, 5, 10, 20, 40):
    test(handbook_turns, OPTIONS, "default")
test(40, WIDE, "16384")

declined = [answer for answer in failed if any(word in answer.lower() for word in DECLINES)]
others = [answer for answer in failed if answer not in declined]
print(f"\n{len(failed)} wrong answers: {len(declined)} said they didn't know or couldn't say, {len(others)} didn't")
for answer in (declined[:3] + others[:3]):
    print(" -", answer.replace("\n", " ")[:110])
