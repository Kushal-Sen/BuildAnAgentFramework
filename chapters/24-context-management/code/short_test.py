"""The short test: 45 turns, five facts, five runs. Nothing, a bigger window, Trim, and one Summarise."""
from library import OPTIONS
from staff_chat import FIVE_QUESTIONS, five_fact_chat
from whitebox import Agent, Retry, Summarise, Trim, load_model

BUDGET = 3000
RUNS = 5
FOR_SUMMARY = {"temperature": 0.2, "num_ctx": 8192}

model = Retry(load_model())  # Chapter 17: a long test should survive a slow reply.


def setup(label):
    """Return the chat to start from, and the agent that will answer."""
    chat = five_fact_chat()
    if label == "nothing":
        return chat, Agent(model, options=OPTIONS)
    if label == "window 16384":
        return chat, Agent(model, options={**OPTIONS, "num_ctx": 16384})
    if label == "Trim":
        return chat, Agent(model, options=OPTIONS, hooks=[Trim(BUDGET)])
    Summarise(model, BUDGET, FOR_SUMMARY).before_model(chat)  # Once per run, then every question uses the note.
    return chat, Agent(model, options=OPTIONS)


names = [name for name, _, _ in FIVE_QUESTIONS]
print(f"{'Setup':<14}" + "".join(f"{name:>9}" for name in names) + f"{'Total':>8}{'Read':>7}")
for label in ("nothing", "window 16384", "Trim", "Summarise"):
    scores, read = dict.fromkeys(names, 0), 0
    for _ in range(RUNS):
        chat, agent = setup(label)
        for name, question, word in FIVE_QUESTIONS:
            result = agent.run(question, history=chat)
            scores[name] += word in result.answer.lower()
            read = result.messages[-1].tokens_in
    total = sum(scores.values())
    print(f"{label:<14}" + "".join(f"{scores[name]:>9}" for name in names) + f"{total:>5}/25{read:>7,}", flush=True)
