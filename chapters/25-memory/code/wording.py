"""The same check in three wordings. How many of Hana's messages does each version pick?"""
from hana import about_hana, chat, recall, right, with_notes
from rewritten import CHECK
from whitebox import Message, load_model

RUNS = 5
NO_RULE = CHECK.replace(" A question is not a fact.", "")
WORDINGS = {
    "as written": CHECK,
    "no question rule": NO_RULE,
    "in passing": NO_RULE.replace("state a fact about the person writing it",
                                  "say anything about the person writing it, even in passing"),
}

model = load_model()
print(f"{'Wording':<17} {'Facts picked':>13} {'Unwanted':>9} {'Recall':>7}")
for label, prompt in WORDINGS.items():
    facts, extra, score = [], [], 0
    for _ in range(RUNS):
        picked = [text for text in chat()
                  if "- " in model.chat([Message("user", prompt.format(text=text))], temperature=0.2).content]
        facts.append(sum(about_hana(text) for text in picked))
        extra.append(len(picked) - facts[-1])
        score += len(right(recall(model, with_notes(picked))))
    print(f"{label:<17} {f'{min(facts)} to {max(facts)}':>13} {f'{min(extra)} to {max(extra)}':>9} {f'{score}/60':>7}", flush=True)
