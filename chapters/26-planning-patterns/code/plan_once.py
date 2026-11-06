"""Run Plan once, and print each thing it did."""
from hop_setups import Counted, OPTIONS, files_seen, handbook_index
from whitebox import Plan, load_model

QUESTION = "I'm a shift lead. How much notice must I give when I resign?"

model = Counted(load_model())
result = Plan(model, handbook_index(), options=OPTIONS).run(QUESTION)
notes = result.messages[1].content.partition("Notes from the search:\n")[2].partition("\n\nQuestion:")[0]

for step, query, note in zip(result.plan, result.queries, notes.split("\n")):
    print("Step: ", step)
    print("Query:", query)
    print("Found:", note)
print("Files:", " ".join(files_seen(result.seen)))
print("Answer:", result.answer)
print("Model calls:", model.calls)
