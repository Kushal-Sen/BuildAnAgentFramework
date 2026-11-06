"""How good is the rough token count? Compare it with what the model really counts, in a window big enough for it all."""
from staff_chat import staff_chat
from whitebox import Message, Retry, load_model, total_tokens

model = Retry(load_model())  # Chapter 17: a long test should survive a slow reply.

print(f"{'Turns':>5} {'Messages':>9} {'Estimate':>9} {'Real':>6} {'Off by':>7}")
for handbook_turns in (0, 5, 20, 40, 80):
    messages = staff_chat(handbook_turns) + [Message("user", "What's my staff number?")]
    # One token of reply, because we only want the count.
    estimate = total_tokens(messages)
    real = model.chat(messages, num_ctx=16384, num_predict=1).tokens_in
    print(f"{handbook_turns + 3:>5} {len(messages):>9} {estimate:>9,} {real:>6,} {(estimate - real) / real:>7.0%}")
