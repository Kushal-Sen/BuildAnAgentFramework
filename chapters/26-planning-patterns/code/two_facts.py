"""Ask the plain agent and Split a question that needs two facts, three times each."""
from hop_setups import Split, build_agent, files_seen, handbook_index, what_it_did
from whitebox import load_model

QUESTION = "I'm a shift lead. How much notice must I give when I resign?"

model = load_model()
index = handbook_index()

for label, setup in (("Plain agent", build_agent(model, index)), ("Split", Split(model, index))):
    print(label)
    for _ in range(3):
        result = setup.run(QUESTION)
        queries, seen = what_it_did(result)
        print("  Searched:", " | ".join(queries))
        print("  Files:   ", " ".join(files_seen(seen)))
        print("  Answer:  ", result.answer[:100].replace("\n", " "))
